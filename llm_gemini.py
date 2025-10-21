"""
Gestion de l'interaction avec le LLM (Gemini)
"""

import streamlit as st
import google.generativeai as genai


class LLMProvider:
    """
    Classe pour interagir avec Gemini (ou autres LLM).
    Facilite le changement de provider à l'avenir.
    """
    
    def __init__(self, api_key: str, provider: str = "gemini", model_name: str = "gemini-2.5-flash"):
        self.provider = provider
        self.api_key = api_key
        
        if provider == "gemini":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Génère une réponse à partir d'un prompt.
        Temperature : 0.0 = déterministe, 1.0 = créatif
        """
        try:
            if self.provider == "gemini":
                # Configuration de génération
                generation_config = {
                    'temperature': temperature,
                    'top_p': 0.8,
                    'top_k': 40
                }
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                # Vérification de la réponse
                if hasattr(response, 'text'):
                    return response.text
                elif hasattr(response, 'parts'):
                    return ''.join([part.text for part in response.parts])
                else:
                    st.error("⚠️ Le LLM a retourné une réponse vide ou bloquée")
                    return ""
            else:
                raise ValueError(f"Provider {self.provider} non supporté")
                
        except Exception as e:
            st.error(f"Erreur LLM: {str(e)}")
            if hasattr(e, 'message'):
                st.error(f"Détails: {e.message}")
            return ""