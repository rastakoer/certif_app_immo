import streamlit as st
from functions import *


#//////////////////////////////////////////////////////////////////////////////
#                          Configuration de la page
#//////////////////////////////////////////////////////////////////////////////

# Définir le titre et le logo de l'application
st.set_page_config(
    page_title="Immo App",
    page_icon=":rocket:",
    layout="wide"
)

# Ajout du style CSS pour supprimer la marge haute
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 0;
        }
        .st-emotion-cache-16txtl3 {
            padding-top: 0;
        }
    </style>
    """,
    unsafe_allow_html=True
)


def main():
    # Connection avec la base de données
    cursor = create_connection(os.environ['DB_HOST'],
                               os.environ['DB_USER'],
                               os.environ['DB_PASSWORD'],
                               int(os.environ['DB_PORT']),
                               "datagouv")
    
    # Affichage du logo
    st.sidebar.markdown("""<div style="display: flex; justify-content: center; align-items: center;">
                        <img src="https://raw.githubusercontent.com/rastakoer/certif_app_immo/application/app/Logo.png" alt="Logo" width="200">
                        </div>""", unsafe_allow_html=True)
    
    valid_formulaire=False
    #//////////////////////////////////////////////////////////////////////////////
    #                          Remplissage du formulaire
    #//////////////////////////////////////////////////////////////////////////////
    # Ajout d'un menu déroulant avec les régions:
    query="""
    SELECT Name_region FROM REGIONS;
    """
    cursor.execute(query)
    resultats = cursor.fetchall()
    liste_regions=[row[0] for row in resultats]

    option_par_defaut = "Sélectionnez une région"
    region = st.sidebar.selectbox("Sélectionnez une région", 
                                [option_par_defaut]+liste_regions)

    if region!="Sélectionnez une région":
        # Ajout d'un menu déroulant avec les départements:
        query=f"""
        SELECT * FROM DEPARTEMENTS AS A
        JOIN (
        SELECT ID_REGION, Name_region
        FROM REGIONS
        )AS B
        ON A.ID_REGION=B.ID_REGION
        WHERE B.Name_region="{region}";
        """
        cursor.execute(query)
        resultats = cursor.fetchall()
        liste_departements=[row[1] for row in resultats]
        option_par_defaut="Sélectionnez un département"
        departement = st.sidebar.selectbox("Sélectionnez un département", 
                                [option_par_defaut]+liste_departements)
        

        if departement!="Sélectionnez un département":
            # Ajout d'un menu déroulant avec les communes
            query=f"""
            SELECT * FROM COMMUNES AS A
            JOIN (
            SELECT ID_DEPT, Name_departement
            FROM DEPARTEMENTS
            )AS B
            ON A.ID_DEPT=B.ID_DEPT
            WHERE B.Name_departement='{departement}';
            """
            cursor.execute(query)
            resultats = cursor.fetchall()
            liste_communes=[row[1] for row in resultats]
            option_par_defaut="Sélectionnez une commune"
            commune = st.sidebar.selectbox("Sélectionnez une commune", 
                                [option_par_defaut]+liste_communes)
            if commune!="Sélectionnez une commune":
                type_de_bien = st.sidebar.selectbox("Sélectionnez le type de logement :", 
                                        ["Faites votre choix"]+["Maison", "Appartement"])
                if type_de_bien!="Faites votre choix":
                    nb_pieces=st.sidebar.selectbox("De combien de pièces est composé le bien", 
                                    [0]+[i for i in range(0,15)])
                    if nb_pieces!=0:
                        surface_bati = st.sidebar.text_input("Surface habitable", "")
                        if surface_bati:
                            if type_de_bien=="Maison":
                                surface_terrain=st.sidebar.text_input("Surface du terrain", "")
                                if surface_terrain:
                                    valid_formulaire = st.sidebar.button("Valider")
                                else:
                                    st.write("Veuillez entrer la surface de votre terrain")
                            else:
                                surface_terrain=0
                                valid_formulaire = st.sidebar.button("Valider")
                        else:
                            st.write ("Veuillez indiquer une surface habitable")
                    else:
                        st.write("Sélectionnez le nombre de pièces")
                else:
                    st.write("Sélectionner un type de bien")
            else:
                st.write("Sélectionnez une commune")
        else:
            st.write("Veuillez choisir un département")
    else:
        st.write("Veuillez choisir une région")


    #//////////////////////////////////////////////////////////////////////////////
    #                          Actions à produire si formulaire valide
    #//////////////////////////////////////////////////////////////////////////////
    if valid_formulaire:
        prediction = api_predict({'SURFACE_BATI' :surface_bati,
                                  'NB_PIECES' : nb_pieces,
                                  'NAME_TYPE_BIEN':type_de_bien,
                                  'Name_region' : region})
        st.title(f"Le bien est estimé à {int(prediction['reponse'])} €")
        # Affichage des ventes réalisées dans la commune
        st.components.v1.html(affichage_ventes_proximite([region,departement,commune]), height=500)
        # cursor.close()
        # db.close()
    else:
        pass

if __name__ == "__main__":
    main()