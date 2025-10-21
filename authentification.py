# ============================================================================
# SYSTÈME D'AUTHENTIFICATION
# ============================================================================

import streamlit as st  # ← CETTE LIGNE DOIT ÊTRE PRÉSENTE


def check_auth():
    """
    Système d'authentification simple.
    Retourne True si l'utilisateur est authentifié.
    """
    def password_entered():
        """Vérifie si le mot de passe est correct"""
        # Récupère le mot de passe depuis les secrets Streamlit
        if "APP_PASSWORD" in st.secrets:
            correct_password = st.secrets["APP_PASSWORD"]
        else:
            # Mot de passe par défaut pour test local
            correct_password = "demo123"
        
        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Supprime le mot de passe de la session
        else:
            st.session_state["password_correct"] = False
        

    # Première visite
    if "password_correct" not in st.session_state:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        st.markdown("### 🔐 Accès restreint")
        st.text_input(
            "Mot de passe", 
            type="password", 
            on_change=password_entered, 
            key="password",
            placeholder="Entrez le mot de passe"
        )
        st.info("💡 Contactez l'administrateur pour obtenir le mot de passe")
        st.markdown("</div>", unsafe_allow_html=True)
        return False
    
    # Mot de passe incorrect
    elif not st.session_state["password_correct"]:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        st.markdown("### 🔐 Accès restreint")
        st.text_input(
            "Mot de passe", 
            type="password", 
            on_change=password_entered, 
            key="password",
            placeholder="Entrez le mot de passe"
        )
        st.error("Mot de passe incorrect")
        st.markdown("</div>", unsafe_allow_html=True)
        return False
    
    # Authentifié avec succès
    else:
        return True