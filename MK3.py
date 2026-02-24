import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(page_title="MacroKiff - Vol 3", layout="centered")

st.title("MacroKiff - volume 3 : ouverture au reste du monde")

# Initialisation des variables de session
if 'essais' not in st.session_state:
    st.session_state.essais = 0
if 'choix_final_valide' not in st.session_state:
    st.session_state.choix_final_valide = False

nom_etudiant = st.text_input("Avant de commencer, veuillez entrer votre Prénom et Nom :")

if nom_etudiant:
    st.write(f"Bienvenue **{nom_etudiant}**. Consigne : maximiser \( Y \) en gardant un déficit budgétaire inférieur à 2% (\( SB/Y \ge -0.02 \)) et un déficit extérieur inférieur à 2% (\( SE/Y \ge -0.02 \)).")
    
    st.subheader("1. Dépenses publiques")
    g0 = st.number_input("Niveau d'investissement public (\( G_0 \)) [0 - 100]", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
    
    st.subheader("2. Recettes fiscales et douanières")
    t0 = st.number_input("Impôt forfaitaire (\( T_0 \)) [0 - 100]", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
    d = st.number_input("Droit de douane (\( d \)) [0 - 1]", min_value=0.0, max_value=1.0, value=0.0, step=0.01)

    def calculer_equilibre(g, t, douane):
        # Résolution du modèle
        denominateur = 0.38 + (0.1 / (1 + douane))
        numerateur = 55 - 0.6 * t + g + (18 / (1 + douane))
        
        revenu_y = numerateur / denominateur
        
        # Calcul des flux internationaux
        m = (2 + 0.1 * revenu_y) / (1 + douane)
        x = 20 / (1 + douane)
        
        # Soldes macroéconomiques
        solde_b = t + (douane * m) - g
        solde_c = x - m # Solde extérieur
        
        return revenu_y, solde_b, solde_c

    if not st.session_state.choix_final_valide:
        # Phase de simulation (5 essais pour le volume 3)
        if st.session_state.essais < 5:
            if st.button(f"Faire une simulation (Essai {st.session_state.essais + 1}/5)"):
                y_eq, sb, bc = calculer_equilibre(g0, t0, d)
                ratio_sb = (sb / y_eq) * 100 if y_eq != 0 else 0
                ratio_bc = (bc / y_eq) * 100 if y_eq != 0 else 0
                
                st.info(f"**Résultats de la simulation :**\n- Revenu (\( Y \)) : {y_eq:.2f}\n- Solde budgétaire : {sb:.2f} ({ratio_sb:.2f}%)\n- Solde extérieur : {bc:.2f} ({ratio_bc:.2f}%)")
                st.session_state.essais += 1
        else:
            st.warning("Vous avez épuisé vos 5 simulations. Il est temps de valider votre choix final.")

        st.markdown("---")
        st.subheader("Décision finale")
        
        # Bouton de validation finale
        if st.button("Valider mon CHOIX FINAL"):
            y_eq, sb, bc = calculer_equilibre(g0, t0, d)
            ratio_sb = (sb / y_eq) if y_eq != 0 else 0
            ratio_bc = (bc / y_eq) if y_eq != 0 else 0
            
            # URL du nouveau formulaire
            form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdOQyBhEKg19gT0Ql0jaiyf8W-FKX71z5i_Y478F30BZ1-vyA/formResponse"
            
            # Association des données aux numéros de colonnes Google Forms avec formatage des virgules
            donnees_formulaire = {
                "entry.1014352347": nom_etudiant,
                "entry.623969476": str(g0).replace('.', ','),
                "entry.1170285416": str(t0).replace('.', ','),
                "entry.5678018": str(d).replace('.', ','),
                "entry.2125479135": str(round(y_eq, 2)).replace('.', ','),
                "entry.26793336": str(round(sb, 2)).replace('.', ','),
                "entry.684617650": str(round(ratio_sb, 4)).replace('.', ','),
                "entry.1239906047": str(round(bc, 2)).replace('.', ','),
                "entry.1034115318": str(round(ratio_bc, 4)).replace('.', ',')
            }
            
            # Envoi avec vérification du statut
            try:
                reponse_google = requests.post(form_url, data=donnees_formulaire)
                
                if reponse_google.status_code == 200:
                    st.success("Choix final enregistré ! Tu découvriras ton résultat et ton classement en cours.")
                    st.session_state.choix_final_valide = True
                else:
                    st.error(f"Erreur d'envoi. Code d'erreur Google : {reponse_google.status_code}.")
            except Exception as e:
                st.error(f"Erreur technique de connexion : {e}")
            
    else:
        st.success("Ta participation a bien été enregistrée. Merci !")