"""
Application principale - Générateur d'État de l'Art Scientifique
Lancez avec: streamlit run main.py
"""

import streamlit as st
import time
import warnings

# Imports configuration
from config_api import *
from history_manager import load_search_history, add_to_history
#from authentification import *

# Imports logique métier
from llm_gemini import LLMProvider
from semantic_scholar_api import SemanticScholarAPI
from article_enricher import ArticleEnricher
from review_generator import ReviewGenerator

# Imports composants UI
from ui_components import *

warnings.filterwarnings('ignore')

# Traitement de l'historique AVANT tout
if 'load_history' in st.session_state:
    st.session_state.question_input_area = st.session_state.load_history
    st.session_state.question = st.session_state.load_history
    del st.session_state.load_history

# Réinitialiser le widget si nouvelle recherche demandée
if st.session_state.get('reset_input', False):
    if 'question_input_area' in st.session_state:
        del st.session_state.question_input_area
    st.session_state.reset_input = False


def init_session_state():
    """Initialise les états de session"""
    defaults = {
        'papers': [],
        'question': "",
        'search_done': False,
        'search_history': load_search_history(),
        'search_strategy': "Automatique",
        'verrous_analysis': None,
        'verrous_validated': False,
        'launch_verrous_search': False,
        'verrous_mode': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main():
    st.set_page_config(
        page_title="Générateur d'État de l'Art",
        page_icon="📚",
        layout="wide"
    )
    
    # ============================================
    # AUTHENTIFICATION EN PREMIER
    # ============================================
    if not check_auth():
        st.stop()
    
    # Initialisation
    init_session_state()
    
    # Affichage
    display_header()
    
    # Sidebar et configuration
    config = display_sidebar(GEMINI_MODELS, DEFAULT_MAX_ARTICLES)
    
  # Vérification de la clé API Gemini (obligatoire)
    gemini_key = st.session_state.get('gemini_api_key', '')
    
    if not gemini_key or gemini_key == '':
        st.warning("⚠️ Configuration requise : Clé API Gemini manquante")
        st.stop()
    
    # Initialisation des composants métier
    llm = LLMProvider(api_key=gemini_key, model_name=config['model_choice'])
    
    ss_key = st.session_state.get('semantic_scholar_api_key', None)
    semantic_api = SemanticScholarAPI(api_key=ss_key if ss_key else None)
    
    core_key = st.session_state.get('core_api_key', None)
    enricher = ArticleEnricher(email="malo.hugd@gmail.com",core_api_key=CORE_API_KEY if CORE_API_KEY != "VOTRE_CLE_CORE_ICI" else None)
    review_generator = ReviewGenerator(llm)
    
    # Zone de saisie
    question, search_button = display_question_input()

    # Gestion du mode Verrous - AVANT la recherche
    if config['search_strategy'] == "Mode Verrous" and not st.session_state.get('verrous_validated'):
        if st.session_state.question and not st.session_state.get('verrous_analysis'):
            # Première fois : extraire les verrous
            with st.spinner("🔧 Analyse CIR et décomposition en verrous..."):
                try:
                    verrous_data = semantic_api.extract_cir_oriented_keywords(
                        st.session_state.question, 
                        llm
                    )
                    st.session_state.verrous_analysis = verrous_data
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
        
        # Afficher l'interface de validation des verrous
        if st.session_state.get('verrous_analysis'):
            verrous_data = st.session_state.verrous_analysis
            
            edited_verrous, edited_keywords, action = display_verrous_interface(verrous_data)
            
            if action == 'add':
                st.session_state.verrous_analysis['verrous'].append('')
                st.session_state.verrous_analysis['keywords_by_verrou'].append([])
                st.rerun()
                
            elif action == 'save':
                st.session_state.verrous_analysis['verrous'] = edited_verrous
                st.session_state.verrous_analysis['keywords_by_verrou'] = edited_keywords
                st.success("✅ Modifications sauvegardées")
                st.rerun()
                
            elif action == 'cancel':
                st.session_state.verrous_analysis = None
                st.session_state.verrous_validated = False
                st.rerun()
                
            elif action == 'search':
                st.session_state.verrous_validated = True
                st.session_state.launch_verrous_search = True
                st.rerun()
            
            st.stop()

    # Logique de recherche
    should_search = False

    if search_button and st.session_state.question:
        st.session_state.search_history = add_to_history(st.session_state.question, st.session_state.search_history)
        st.session_state.search_strategy = config['search_strategy']
        should_search = True

    if st.session_state.get('launch_verrous_search'):
        should_search = True
        st.session_state.launch_verrous_search = False

    if should_search:        
        papers = perform_search(
            config=config,
            question=st.session_state.question,
            semantic_api=semantic_api,
            llm=llm
        )
                
        if papers:
            enricher = ArticleEnricher(
                email="malo.hugd@gmail.com",
                core_api_key=CORE_API_KEY if CORE_API_KEY != "VOTRE_CLE_CORE_ICI" else None
            )
            papers_sorted = display_enrichment_progress(papers, enricher, ENRICHMENT_TIMEOUT)
            
            # Génération des résumés
            papers_sorted = generate_summaries(papers_sorted, review_generator)
            
            st.session_state.papers = papers_sorted
            st.session_state.search_done = True

#demande d'ajout manuel de DOI
    display_manual_doi_section(
        semantic_api=semantic_api,
        enricher=enricher,  # ou enricher, selon votre variable
        review_generator=review_generator,
        ENRICHMENT_TIMEOUT=ENRICHMENT_TIMEOUT
    )
    
    # Affichage des résultats
    if st.session_state.search_done and st.session_state.papers:
        selected_papers = display_papers_selection(
            papers=st.session_state.papers,
            question=st.session_state.question,
            verrous_validated=st.session_state.get('verrous_validated', False),
            verrous_analysis=st.session_state.get('verrous_analysis')
        )
        
        # Génération de l'état de l'art
        display_review_generation(selected_papers, review_generator)


def perform_search(config, question, semantic_api, llm):
    """
    Effectue la recherche selon la stratégie choisie
    
    Returns:
        List[Dict]: Articles trouvés
    """
    if config['search_strategy'] == "Automatique":
        return perform_automatic_search(config, question, semantic_api, llm)
    else:
        return perform_verrous_search(config, question, semantic_api, llm)


def perform_automatic_search(config, question, semantic_api, llm):
    """Recherche automatique (FUNDAMENTAL/APPLIED/EXPERIMENTAL)"""
    
    try:
        # 1. Analyser le type de question
        with st.spinner("Analyse de la question..."):
            analysis = semantic_api.analyze_question_type(question, llm)
            st.session_state.question_analysis = analysis
        
        # Afficher l'analyse
        display_analysis_metrics(analysis)
        
        # 2. Extraire les mots-clés selon la stratégie
        with st.spinner("Extraction des mots-clés..."):
            keywords = semantic_api.extract_keywords_by_strategy(
                question, 
                llm, 
                strategy=analysis['strategy']
            )
        
        st.caption(f"🔑 Mots-clés : {', '.join(keywords[:5])}...")
        
        # 3. Rechercher les articles
        all_papers = []
        
        with st.spinner("Recherche d'articles scientifiques..."):
            if analysis['strategy'] == 'fundamental':
                query = ' '.join(keywords[:6])
                papers = semantic_api.search_papers(
                    query=query,
                    limit=config['max_articles'],
                    year_start=config.get('year_start'),
                    year_end=config.get('year_end')
                )
                all_papers.extend(papers)
                
            elif analysis['strategy'] == 'applied':
                tech_keywords = keywords[:4]
                general_keywords = keywords[4:8]
                
                papers1 = semantic_api.search_papers(
                    query=' '.join(tech_keywords),
                    limit=config['max_articles'] // 2,
                    year_start=config.get('year_start'),
                    year_end=config.get('year_end')
                )
                
                time.sleep(3)  # ← ATTENDRE 2 secondes entre les requêtes

                papers2 = semantic_api.search_papers(
                    query=' '.join(general_keywords),
                    limit=config['max_articles'] // 2,
                    year_start=config.get('year_start'),
                    year_end=config.get('year_end')
                )
                
                all_papers.extend(papers1)
                all_papers.extend(papers2)
                
            else:  # experimental
                chunk_size = 3
                for i in range(0, len(keywords), chunk_size):
                    if i > 0:
                        time.sleep(4)  # Attendre X secondes entre chaque requête
                    chunk = keywords[i:i+chunk_size]
                    papers = semantic_api.search_papers(
                        query=' '.join(chunk),
                        limit=config['max_articles'] // 4,
                        year_start=config.get('year_start'),
                        year_end=config.get('year_end')
                    )
                    all_papers.extend(papers)
        
        # Dédupliquer par paperId
        seen_ids = set()
        unique_papers = []
        for paper in all_papers:
            paper_id = paper.get('paperId')
            if paper_id and paper_id not in seen_ids:
                seen_ids.add(paper_id)
                unique_papers.append(paper)
        
        if unique_papers:
            return unique_papers[:config['max_articles']]
        else:
            st.warning("⚠️ Aucun article trouvé")
            return []
            
    except Exception as e:
        st.error(f"❌ Erreur lors de la recherche: {str(e)}")
        return []


def perform_verrous_search(config, question, semantic_api, llm):
    """Recherche par verrous techniques (Mode CIR)"""
    st.info("🔧 Analyse CIR et décomposition en verrous...")
    
    try:
        # 1. Extraire les verrous CIR
        verrous_data = semantic_api.extract_cir_oriented_keywords(question, llm)
        st.session_state.verrous_analysis = verrous_data
        
        # 2. Afficher l'interface de validation des verrous
        edited_verrous, edited_keywords, action = display_verrous_interface(verrous_data)
        
        if action == 'add':
            # Ajouter un nouveau verrou
            verrous_data['verrous'].append('')
            verrous_data['keywords_by_verrou'].append([])
            st.rerun()
            
        elif action == 'save':
            # Sauvegarder les modifications
            verrous_data['verrous'] = edited_verrous
            verrous_data['keywords_by_verrou'] = edited_keywords
            st.session_state.verrous_analysis = verrous_data
            st.success("✅ Modifications sauvegardées")
            
        elif action == 'cancel':
            # Annuler et retourner
            st.session_state.verrous_analysis = None
            st.session_state.verrous_validated = False
            st.rerun()
            
        elif action == 'search':
            # Lancer la recherche par verrous
            st.session_state.verrous_validated = True
            
            all_papers = []
            
            # Rechercher pour chaque verrou
            for i, (verrou, keywords) in enumerate(zip(edited_verrous, edited_keywords)):
                if verrou and keywords:
                    st.info(f"🔍 Recherche pour le verrou {i+1}/{len(edited_verrous)}")
                    
                    # Recherche avec les mots-clés du verrou
                    papers = semantic_api.search_papers(
                        query=' '.join(keywords),
                        limit=config['max_articles'] // len(edited_verrous),
                        year_start=config.get('year_start'),
                        year_end=config.get('year_end')
                    )
                    all_papers.extend(papers)
            
            # Dédupliquer
            seen_ids = set()
            unique_papers = []
            for paper in all_papers:
                paper_id = paper.get('paperId')
                if paper_id and paper_id not in seen_ids:
                    seen_ids.add(paper_id)
                    unique_papers.append(paper)
            
            if unique_papers:
                st.success(f"✅ {len(unique_papers)} articles uniques trouvés via les verrous")
                return unique_papers[:config['max_articles']]
            else:
                st.warning("⚠️ Aucun article trouvé")
                return []
        
        # Si on n'a pas lancé la recherche, retourner None
        return None
            
    except Exception as e:
        st.error(f"❌ Erreur lors de la recherche par verrous: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return []


def generate_summaries(papers, review_generator):
    """Génère les résumés des articles"""
    with st.spinner("✍️ Génération des résumés..."):
        for i, paper in enumerate(papers):
            if i > 0:
                time.sleep(1.0)
            try:
                paper['summary'] = review_generator.summarize_paper(paper)
            except Exception as e:
                st.warning(f"⚠️ Erreur: {str(e)}")
                paper['summary'] = "Erreur de génération."
    
    return papers

def display_review_generation(selected_papers, review_generator):
    """Affiche la section de génération de l'état de l'art"""
    st.header("3️⃣ Génération de l'état de l'art")
    
    if st.button("📝 Générer l'état de l'art complet", type="primary", disabled=len(selected_papers) == 0):
        if len(selected_papers) == 0:
            st.warning("⚠️ Veuillez sélectionner au moins un article")
        else:
            with st.spinner("✨ Génération en cours..."):
                try:
                    review = review_generator.generate_full_review(selected_papers, st.session_state.question)
                    
                    if review and review.strip():
                        st.success("✅ État de l'art généré !")
                        st.markdown("---")
                        st.markdown("## 📑 État de l'art")
                        st.markdown(review)
                        
                        st.download_button(
                            label="💾 Télécharger",
                            data=review,
                            file_name="etat_de_lart.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("❌ La génération a échoué")
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    main()
