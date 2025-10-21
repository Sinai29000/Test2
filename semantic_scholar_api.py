"""
Interaction avec l'API Semantic Scholar
"""

import requests
import streamlit as st
from typing import List, Dict, Optional
from config_api import SEMANTIC_SCHOLAR_BASE_URL


class SemanticScholarAPI:
    """Gère les interactions avec l'API Semantic Scholar"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = SEMANTIC_SCHOLAR_BASE_URL
        self.api_key = api_key
        self.headers = {}
        
        # Si une clé API est fournie, l'ajouter aux headers
        if self.api_key:
            self.headers['x-api-key'] = self.api_key
    
    def analyze_question_type(self, question: str, llm) -> Dict[str, any]:
        """
        Analyse le type de question pour adapter la stratégie
        Score > 7 = FUNDAMENTAL, Score > 4 = APPLIED, Score ≤ 4 = EXPERIMENTAL
        """
        prompt = f"""
        Analysez cette question de recherche et donnez UNIQUEMENT un score de technicité.

        Question: {question}

        Donnez un score de 0 à 10 selon ces critères :
        - 8-10 : Recherche fondamentale pure (algorithmes théoriques, méthodologies scientifiques, mathématiques avancées)
        - 5-7 : Recherche appliquée (solutions techniques innovantes, méthodologies applicables, optimisations)
        - 0-4 : Développement expérimental (systèmes industriels, outils métier, intégration de technologies existantes)

        Répondez UNIQUEMENT avec le chiffre du score, rien d'autre.

        Exemples :
        "Quels sont les algorithmes de deep learning pour la vision par ordinateur ?" → 9
        "Comment optimiser un système de recommandation e-commerce ?" → 6
        "Comment développer une plateforme collaborative pour la gestion qualité ?" → 3
        """
        
        response = llm.generate(prompt).strip()
        
        try:
            # Extraire le score
            tech_score = float(response.split()[0])  # Prend le premier nombre
            
            # Déterminer le type selon le score
            if tech_score > 7:
                question_type = 'FUNDAMENTAL'
                strategy = 'fundamental'
            elif tech_score > 4:
                question_type = 'APPLIED'
                strategy = 'applied'
            else:
                question_type = 'EXPERIMENTAL'
                strategy = 'experimental'
            
            return {
                'type': question_type,
                'tech_score': tech_score,
                'strategy': strategy
            }
        except:
            # Fallback par défaut
            return {
                'type': 'EXPERIMENTAL',
                'tech_score': 3,
                'strategy': 'experimental'
            }


    def extract_keywords_by_strategy(self, question: str, llm, strategy: str = 'experimental') -> List[str]:
        """
        Extrait les mots-clés selon la stratégie détectée
        """
        if strategy == 'fundamental':
            return self._extract_keywords_fundamental(question, llm)
        elif strategy == 'applied':
            return self._extract_keywords_applied(question, llm)
        else:  # experimental
            return self._extract_keywords_experimental(question, llm)
    
    def _extract_keywords_fundamental(self, question: str, llm) -> List[str]:
        """R&D PURE : Mots-clés techniques précis"""
        prompt = f"""
        Analysez cette question de recherche FONDAMENTALE et extrayez 4-6 mots-clés TECHNIQUES très PRÉCIS en anglais.

        Question: {question}

        Concentrez-vous uniquement sur les termes scientifiques et théoriques spécifiques.

        IMPORTANT: Répondez UNIQUEMENT avec les mots-clés séparés par des virgules, sans explication.

        Exemple: transformer architecture, attention mechanism, neural network optimization
        """
        response = llm.generate(prompt)
        keywords = [kw.strip() for kw in response.split(',')]
        return keywords[:6]
    
    def _extract_keywords_applied(self, question: str, llm) -> List[str]:
        """R&D APPLIQUÉE : Mix de termes techniques et généraux"""
        prompt = f"""
        Analysez cette question de recherche APPLIQUÉE et extrayez 5-8 mots-clés en anglais.
        Mélangez des termes TECHNIQUES (3-4) et des termes GÉNÉRAUX/DOMAINE (2-4).

        Question: {question}

        IMPORTANT: Répondez UNIQUEMENT avec les mots-clés séparés par des virgules, sans explication.

        Exemple: machine learning, quality control, manufacturing process, predictive maintenance, automation
        """
        response = llm.generate(prompt)
        keywords = [kw.strip() for kw in response.split(',')]
        return keywords[:8]
    
    def _extract_keywords_experimental(self, question: str, llm) -> List[str]:
        """DÉVELOPPEMENT EXPÉRIMENTAL : Décomposition en sous-problématiques + mots-clés variés"""
        prompt = f"""
        Analysez cette question de DÉVELOPPEMENT EXPÉRIMENTAL industriel.

        Question: {question}

        Identifiez 3-4 SOUS-PROBLÉMATIQUES scientifiques/techniques recherchables, puis pour CHAQUE sous-problématique, donnez 2-3 mots-clés en anglais.

        Format de réponse (STRICT):
        Sous-problématique 1: keyword1, keyword2, keyword3
        Sous-problématique 2: keyword1, keyword2, keyword3
        Sous-problématique 3: keyword1, keyword2, keyword3

        IMPORTANT: Respectez exactement ce format.
        """
        response = llm.generate(prompt)
        
        # Parse les sous-problématiques et mots-clés
        all_keywords = []
        lines = response.split('\n')
        
        for line in lines:
            if ':' in line:
                # Extrait les mots-clés après le ":"
                keywords_part = line.split(':', 1)[1]
                keywords = [kw.strip() for kw in keywords_part.split(',')]
                all_keywords.extend(keywords)
        
        return all_keywords[:12]  # Max 12 mots-clés pour recherche large
    
    def search_papers(self, query: str, limit: int = 15, year_start: int = None, year_end: int = None) -> List[Dict]:
        """
        Recherche des articles sur Semantic Scholar avec filtre de dates optionnel.
        """
        url = f"{self.base_url}/paper/search"
        
        # Ajouter le filtre de dates à la requête si spécifié
        search_query = query
        if year_start is not None or year_end is not None:
            if year_start and year_end:
                search_query = f"{query} year:{year_start}-{year_end}"
            elif year_start:
                search_query = f"{query} year:{year_start}-"
            elif year_end:
                search_query = f"{query} year:-{year_end}"
        
        params = {
            'query': search_query,
            'limit': limit,
            'fields': 'title,abstract,authors,year,citationCount,publicationDate,url,paperId,tldr,openAccessPdf,externalIds'
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if not self.api_key:
                st.info("ℹ️ Recherche sans clé API (limites réduites)")

            
            return data.get('data', [])
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                st.error("⚠️ Limite de taux atteinte.")
                time.sleep(5)
                return []
            else:
                st.error(f"Erreur API Semantic Scholar: {str(e)}")
            return []
            
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur API: {str(e)}")
            return []
    
    def get_paper_details(self, paper_id: str) -> Optional[Dict]:
        """
        Récupère les détails complets d'un article spécifique.
        """
        url = f"{self.base_url}/paper/{paper_id}"
        params = {
            'fields': 'title,abstract,authors,year,citationCount,references,citations,url,tldr,openAccessPdf,externalIds'
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur lors de la récupération de l'article: {str(e)}")
            return None

    def get_paper_by_doi(self, doi: str) -> Optional[Dict]:
        """
        Récupère un article spécifique via son DOI
        """
        url = f"{self.base_url}/paper/DOI:{doi}"
        params = {
            'fields': 'title,abstract,authors,year,citationCount,publicationDate,url,paperId,tldr,openAccessPdf,externalIds'
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            paper = response.json()
            
            # S'assurer que externalIds contient le DOI
            if not paper.get('externalIds'):
                paper['externalIds'] = {}
            if 'DOI' not in paper['externalIds']:
                paper['externalIds']['DOI'] = doi
            
            return paper
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                st.error(f"❌ Article non trouvé pour le DOI: {doi}")
            else:
                st.error(f"❌ Erreur API: {e.response.status_code}")
            return None
            
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Erreur de connexion: {str(e)}")
            return None
        
    def extract_cir_oriented_keywords(self, question: str, llm) -> dict:
        """
        Extraction CIR : identifie les verrous techniques contextualisés
        """
        prompt = f"""
        Vous êtes un expert en dossiers CIR (Crédit d'Impôt Recherche).

        Analysez ce projet de développement expérimental industriel :
        "{question}"

        Effectuez une analyse en 3 parties :

        **PARTIE 1 - CONTEXTE INDUSTRIEL**
        En 1-2 phrases : quel est le contexte métier, le domaine d'application et l'objectif pratique ?

        **PARTIE 2 - VERROUS TECHNIQUES GÉNÉRALISABLES**
        Identifiez 3-4 VERROUS SCIENTIFIQUES/TECHNIQUES qui sous-tendent ce projet.

        Chaque verrou doit inclure :
        - La problématique technique
        - Les contraintes spécifiques (performance, réglementation, compatibilité, etc.)
        - Le contexte d'application

        Format:
        1. [Description complète du verrou avec contraintes et contexte]
        2. [Description complète du verrou avec contraintes et contexte]
        3. [Description complète du verrou avec contraintes et contexte]

        **PARTIE 3 - MOTS-CLÉS ACADÉMIQUES PAR VERROU**
        Pour CHAQUE verrou, donnez 3-4 mots-clés de recherche EN ANGLAIS.

        Mélangez :
        - Concepts scientifiques/techniques
        - Domaines d'application
        - Méthodes/technologies

        Format:
        1. keyword1, keyword2, keyword3, keyword4
        2. keyword1, keyword2, keyword3, keyword4
        3. keyword1, keyword2, keyword3, keyword4

        Répondez en suivant EXACTEMENT ce format.
        """
        
        response = llm.generate(prompt)
        
        # Parse la réponse
        lines = [l.strip() for l in response.split('\n') if l.strip()]
        
        context = ""
        verrous = []
        keywords_by_verrou = []
        
        current_section = None
        
        for line in lines:
            if "PARTIE 1" in line or "CONTEXTE" in line:
                current_section = "context"
                continue 
            elif "PARTIE 2" in line or "VERROUS" in line:
                current_section = "verrous"
                continue
            elif "PARTIE 3" in line or "MOTS-CLÉS" in line:
                current_section = "keywords"
                continue
            
            if current_section == "context" and line and not line.startswith("**"):
                context += line + " "
            
            elif current_section == "verrous" and line and line[0].isdigit():
                verrou = line.split('.', 1)[1].strip() if '.' in line else line
                verrous.append(verrou)
            
            elif current_section == "keywords" and line and line[0].isdigit():
                kw_list = line.split('.', 1)[1].strip() if '.' in line else line
                keywords = [k.strip() for k in kw_list.split(',')]
                keywords_by_verrou.append(keywords)
        
        # Fallback si parsing échoue
        if not verrous or not keywords_by_verrou:
            return {
                'context': question,
                'verrous': ['Verrou technique général'],
                'keywords_by_verrou': [['software', 'development', 'system', 'optimization']],
                'all_keywords': ['software', 'development', 'system', 'optimization']
            }
        
        # Compile tous les mots-clés
        all_keywords = []
        for kw_list in keywords_by_verrou:
            all_keywords.extend(kw_list)
        
        return {
            'context': context.strip(),
            'verrous': verrous[:4],
            'keywords_by_verrou': keywords_by_verrou[:4],
            'all_keywords': all_keywords[:16]
        }