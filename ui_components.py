""""
Composants d'interface utilisateur pour l'application Streamlit - Version Ymaje Partners
Optimisé pour sobriété et facilité d'accès
"""

import streamlit as st
import time
from typing import List, Dict
import config_api

# ============================================================================
# CONFIGURATION YMAJE PARTNERS - CHARTE GRAPHIQUE
# ============================================================================

# Couleurs Ymaje Partners
COLOR_PRIMARY = "#163058"      # Bleu marine principal
COLOR_SECONDARY = "#3E3B90"    # Bleu violet
COLOR_ACCENT = "#A7864D"       # Or/Bronze

# Configuration logos (désactivés par défaut pour sobriété)
SHOW_MAIN_LOGO = False
SHOW_FOOTER_LOGOS = False

def inject_ymaje_css():
    """Applique le style Ymaje Partners à l'application"""
    st.markdown(f"""
    <style>
        /* Police Caviar Dreams - fallback vers system */
        @import url('https://fonts.cdnfonts.com/css/caviar-dreams');
        
        html, body, [class*="css"] {{
            font-family: 'Caviar Dreams', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        /* Boutons principaux */
        .stButton > button {{
            background-color: {COLOR_PRIMARY} !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY} !important;
            box-shadow: 0 4px 12px rgba(22, 48, 88, 0.2) !important;
        }}
        
        /* Métriques personnalisées */
        [data-testid="stMetricValue"] {{
            color: {COLOR_PRIMARY} !important;
            font-weight: 600 !important;
        }}
        
        /* Checkboxes et radios */
        .stCheckbox label, .stRadio label {{
            color: {COLOR_PRIMARY} !important;
        }}
        
        /* Sliders - Style neutre */
        .stSlider [data-baseweb="slider-track"] {{
            background: linear-gradient(to right, {COLOR_PRIMARY} 0%, {COLOR_PRIMARY} var(--value), #e0e0e0 var(--value), #e0e0e0 100%) !important;
        }}

        .stSlider [role="slider"] {{
            background-color: {COLOR_PRIMARY} !important;
            border: 2px solid white !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: {COLOR_PRIMARY} !important;
            font-weight: 600 !important;
        }}

        /* Sous-titres h4 en gris */
        h4 {{
            color: #666 !important;
            font-weight: 400 !important;
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background-color: #f8f9fa !important;
            border-left: none !important;
            font-weight: 500 !important;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: #fafbfc !important;
        }}
        
        /* Info boxes */
        .stAlert {{
            border-left: 4px solid {COLOR_ACCENT} !important;
        }}
        
        /* Masquer les conteneurs vides qui créent des barres grises */
        .element-container:empty {{
            display: none !important;
        }}
        
        div[data-testid="stVerticalBlock"] > div:empty {{
            display: none !important;
        }}
        
        .stMarkdown:empty {{
            display: none !important;
        }}

        /* SUPPRESSION des éléments Streamlit natifs - SAUF menu et bouton sidebar */
        footer {{visibility: hidden !important;}}
        
        /* Suppression du texte "Made with Streamlit" et autres */
        .viewerBadge_container__1QSob {{display: none !important;}}
        .styles_viewerBadge__1yB5_ {{display: none !important;}}
        .viewerBadge_link__1S137 {{display: none !important;}}
        .viewerBadge_text__1JaDK {{display: none !important;}}
        
        /* FORCER l'affichage du bouton hamburger et toggle sidebar */
        button[data-testid="collapsedControl"] {{
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }}
        
        section[data-testid="stSidebarNav"] {{
            display: block !important;
            visibility: visible !important;
        }}
        
        /* Espacement harmonieux */
        .block-container {{
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def display_header():
    """Affiche l'en-tête sobre et professionnel avec logos Ymaje"""
    inject_ymaje_css()
    
    # Supprimer les gaps entre colonnes
    st.markdown("""
    <style>
    [data-testid="column"] {
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header avec logos de part et d'autre
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        try:
            st.markdown("<div style='display: flex; align-items: center; justify-content: center; height: 100%; padding-top: 20px;'>", unsafe_allow_html=True)
            st.image("Images/VIGNETTE_marine.png", width=100)
            st.markdown("</div>", unsafe_allow_html=True)
        except:
            st.write("")
    
    with col2:
        st.markdown(f"""
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; padding: 1rem 0; margin: 0;'>
            <h1 style='color: {COLOR_PRIMARY}; font-size: 3rem; margin: 0; padding: 0; text-align: center;'>
                État de l'Art Scientifique
            </h1>
            <h4 style='color: #666 !important; font-size: 1.2rem; margin: 0.5rem 0 0 0; padding: 0; text-align: center;'>
                Recherche académique et développement expérimental
            </h4>
        </div>
        """, unsafe_allow_html=True)

def display_sidebar(gemini_models: List[str], default_max_articles: int):
    """
    Sidebar épurée avec configuration essentielle
    
    Returns:
        dict: Configuration sélectionnée par l'utilisateur
    """
    with st.sidebar:

        st.markdown(f"""
        <h1 style='color: {COLOR_PRIMARY}; font-size: 1rem; margin-bottom: 0rem; text-align: left;'>
            ⚙️ Configuration
        </h1>
        """, unsafe_allow_html=True)
        
        # ========================================
        # SECTION CLÉS API avec détection auto
        # ========================================
        _display_api_keys_section()
        
        st.markdown("---")
        
        # Stratégie de recherche
        st.markdown("**Stratégie de recherche**")
        search_strategy = st.radio(
            "Type d'analyse",
            options=["Automatique", "Mode Verrous"],
            index=0,
            help="Automatique : détection intelligente | Mode Verrous : décomposition technique",
            label_visibility="collapsed",
            key="search_strategy_radio"
        )
        
        # Modèle et paramètres
        model_choice = st.selectbox(
            "Modèle Gemini",
            options=gemini_models,
            index=0,
            key="model_choice_select"
        )
                
        # Stratégie de recherche - MÊME STYLE que "Statut des API"
        st.markdown("**Stratégie de recherche**")
        
        search_strategy = st.radio(
            "Type d'analyse",
            options=["Automatique", "Mode Verrous"],
            index=0,
            help="Automatique : détection intelligente | Mode Verrous : décomposition technique",
            label_visibility="collapsed"
        )
        
        # Modèle et paramètres
        model_choice = st.selectbox(
            "Modèle Gemini",
            options=gemini_models,
            index=0
        )
        
        max_articles = st.slider(
            "Nombre d'articles",
            min_value=5,
            max_value=25,
            value=default_max_articles,
            key="max_articles_slider"
        )
        
        # Filtre dates
        st.markdown("---")
        date_filter_config = _display_date_filter_compact()
        
        # Historique
        _display_search_history()
    
    return {
        'search_strategy': search_strategy,
        'model_choice': model_choice,
        'max_articles': max_articles,
        'year_start': date_filter_config['year_start'],
        'year_end': date_filter_config['year_end']
    }

# def _display_api_status_compact():
#     """Version compacte du statut API - affichage vertical sans espaces"""
#     st.markdown("**Statut des API**")
    
#     # Gemini
#     if config_api.GEMINI_API_KEY and config_api.GEMINI_API_KEY != "VOTRE_CLE_GEMINI_ICI":
#         st.markdown("<small style='color: #28a745; line-height: 1.2; margin: 0;'>✓ Gemini</small>", unsafe_allow_html=True)
#     else:
#         st.markdown("<small style='color: #dc3545; line-height: 1.2; margin: 0;'>✗ Gemini</small>", unsafe_allow_html=True)
    
#     # Semantic Scholar
#     if config_api.SEMANTIC_SCHOLAR_API_KEY != "VOTRE_CLE_SEMANTIC_SCHOLAR_ICI":
#         st.markdown("<small style='color: #28a745; line-height: 1.2; margin: 0;'>✓ Semantic Scholar</small>", unsafe_allow_html=True)
#     else:
#         st.markdown("<small style='color: #999; line-height: 1.2; margin: 0;'>○ Semantic Scholar</small>", unsafe_allow_html=True)
    
#     # CORE
#     if config_api.CORE_API_KEY != "VOTRE_CLE_CORE_ICI":
#         st.markdown("<small style='color: #28a745; line-height: 1.2; margin: 0;'>✓ CORE</small>", unsafe_allow_html=True)
#     else:
#         st.markdown("<small style='color: #ffc107; line-height: 1.2; margin: 0;'>○ CORE</small>", unsafe_allow_html=True)

def _display_date_filter_compact():
    """Version compacte du filtre de dates"""
    enable_date_filter = st.checkbox("Filtrer par période", value=False)
    
    if enable_date_filter:
        col1, col2 = st.columns(2)
        with col1:
            year_start = st.number_input("De", min_value=1900, max_value=2025, value=2015, step=1)
        with col2:
            year_end = st.number_input("À", min_value=1900, max_value=2025, value=2025, step=1)
        
        if year_start > year_end:
            st.warning("⚠️ Période invalide")
    else:
        year_start = None
        year_end = None
    
    return {'year_start': year_start, 'year_end': year_end}


def _display_search_history():
    """Historique des recherches"""
    if st.session_state.get('search_history'):
        st.markdown("---")
        st.markdown("**Historique**")
        
        if st.button("Effacer", key="clear_history", use_container_width=True):
            from history_manager import save_search_history
            st.session_state.search_history = []
            save_search_history([])
            st.rerun()
        
        for idx, hist_q in enumerate(st.session_state.search_history[:5]):
            if st.button(f"{hist_q[:40]}...", 
                       key=f"history_{idx}", 
                       use_container_width=True,
                       help=hist_q):
                st.session_state.load_history = hist_q
                st.rerun()

def display_question_input():
    """Zone de saisie épurée"""
    st.markdown(f"""
    <h2 style='color: {COLOR_PRIMARY}; font-size: 1.4rem; margin: 2rem 0 1rem 0;'>
        Votre question de recherche
    </h2>
    """, unsafe_allow_html=True)
    
    question = st.text_area(
        "Question technique",
        placeholder="Exemple : Quelles sont les méthodes d'apprentissage par renforcement pour la robotique collaborative ?",
        height=100,
        key="question_input_area",
        label_visibility="collapsed"
    )
    
    # Synchroniser
    st.session_state.question = question
    
    col1, col2 = st.columns([1, 5])
    with col1:
        search_button = st.button("Rechercher", type="primary")
    with col2:
        if st.session_state.get('search_done'):
            if st.button("Nouvelle recherche"):
                st.session_state.papers = []
                st.session_state.search_done = False
                st.session_state.verrous_analysis = None
                st.session_state.verrous_validated = False
                st.session_state.question = ''
                st.session_state.reset_input = True  # Flag pour réinitialiser
                st.rerun()
    
    return question, search_button

def display_analysis_metrics(analysis: Dict):
    """Métriques d'analyse - version sobre"""
    
    col1, col2, col3 = st.columns(3)
    
    type_emoji = {"FUNDAMENTAL": "🔬", "APPLIED": "🔧", "EXPERIMENTAL": "🏭"}
    
    with col1:
        st.metric("Type", f"{type_emoji.get(analysis['type'], '🔬')} {analysis['type']}")
    with col2:
        st.metric("Score technique", f"{analysis['tech_score']:.0f}/10")
    with col3:
        strategy_labels = {
            'fundamental': 'Précise',
            'applied': 'Élargie',
            'experimental': 'Multi-angles'
        }
        st.metric("Stratégie", strategy_labels[analysis['strategy']])
    
    st.markdown("</div>", unsafe_allow_html=True)


def display_verrous_interface(verrous_data: Dict):
    """Interface verrous - version optimisée"""
    st.markdown(f"""
    <h2 style='color: {COLOR_PRIMARY}; font-size: 1.4rem; margin: 2rem 0 1rem 0;'>
        🔧 Décomposition en verrous techniques
    </h2>
    """, unsafe_allow_html=True)
    
    st.info(f"**Contexte identifié :** {verrous_data.get('context', 'N/A')}")
    
    edited_verrous = []
    edited_keywords = []
    
    num_verrous = len(verrous_data.get('verrous', []))
    
    for i in range(num_verrous):
        with st.expander(f"Verrou {i+1}", expanded=(i < 2)):  # Seulement 2 premiers ouverts
            verrou_text = st.text_area(
                "Description",
                value=verrous_data['verrous'][i] if i < len(verrous_data['verrous']) else '',
                height=80,
                key=f"verrou_{i}"
            )
            edited_verrous.append(verrou_text)
            
            keywords = verrous_data['keywords_by_verrou'][i] if i < len(verrous_data['keywords_by_verrou']) else []
            keywords_str = ', '.join(keywords)
            keywords_input = st.text_input(
                "Mots-clés (EN)",
                value=keywords_str,
                key=f"keywords_verrou_{i}",
                help="3-4 mots-clés en anglais"
            )
            edited_keywords.append([k.strip() for k in keywords_input.split(',') if k.strip()])
    
    # Actions
    col1, col2, col3 = st.columns(3)
    
    action = None
    
    with col1:
        if st.button("➕ Ajouter", use_container_width=True):
            action = 'add'
    
    with col2:
        if st.button("💾 Sauvegarder", use_container_width=True):
            action = 'save'
    
    with col3:
        if st.button("❌ Annuler", use_container_width=True):
            action = 'cancel'
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔍 Lancer la recherche", type="primary", use_container_width=True):
        action = 'search'
    
    return edited_verrous, edited_keywords, action


def display_enrichment_progress(papers: List[Dict], enricher, timeout: int):
    """Barre de progression épurée"""
    with st.spinner("Enrichissement en cours..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        enrichment_start = time.time()
        papers_sorted = sorted(papers, key=lambda x: x.get('citationCount', 0), reverse=True)
        
        for idx, paper in enumerate(papers_sorted):
            elapsed = time.time() - enrichment_start
            if elapsed > timeout:
                status_text.warning(f"Timeout ({timeout}s)")
                for remaining_paper in papers_sorted[idx:]:
                    if 'enrichment_status' not in remaining_paper:
                        remaining_paper['enrichment_status'] = 'timeout'
                        remaining_paper['source_quality'] = '🔴'
                break
            
            progress = (idx + 1) / len(papers_sorted)
            progress_bar.progress(progress)
            status_text.text(f"Article {idx + 1}/{len(papers_sorted)}")
            
            paper = enricher.enrich_paper(paper, enrichment_start, timeout)
            time.sleep(0.3)
        
        progress_bar.empty()
        status_text.empty()
        
        # Stats compactes
        complete = sum(1 for p in papers_sorted if p.get('source_quality') == '🟢')
        partial = sum(1 for p in papers_sorted if p.get('source_quality') == '🟡')
        failed = sum(1 for p in papers_sorted if p.get('source_quality') == '🔴')
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", len(papers_sorted))
        with col2:
            st.metric("🟢 Complets", complete)
        with col3:
            st.metric("🟡 Partiels", partial)
        with col4:
            st.metric("🔴 Limités", failed)
    
    return papers_sorted


def display_papers_selection(papers: List[Dict], question: str, verrous_validated: bool = False, verrous_analysis: Dict = None):
    """Liste d'articles épurée et lisible"""
    st.markdown(f"""
    <h2 style='color: {COLOR_PRIMARY}; font-size: 1.4rem; margin: 2rem 0 1rem 0;'>
        Articles trouvés
    </h2>
    """, unsafe_allow_html=True)
    
    # Badge de méthode
    if verrous_validated:
        st.markdown(f"<div style='background: {COLOR_SECONDARY}; color: white; padding: 0.5rem 1rem; border-radius: 6px; display: inline-block; margin-bottom: 1rem;'>Mode VERROUS activé</div>", unsafe_allow_html=True)
    else:
        analysis = st.session_state.get('question_analysis', {})
        strategy_type = analysis.get('type', 'Automatique')
        st.markdown(f"<div style='background: {COLOR_PRIMARY}; color: white; padding: 0.5rem 1rem; border-radius: 6px; display: inline-block; margin-bottom: 1rem;'>Stratégie : {strategy_type}</div>", unsafe_allow_html=True)
    
    st.markdown(f"**Question :** {question}")
    st.markdown("<br>", unsafe_allow_html=True)
    
    selected_papers = []
    
    for i, paper in enumerate(papers):
        manual_badge = "➕ " if paper.get('manually_added') else ""
        
        with st.expander(
            f"{manual_badge}{paper.get('title', 'Sans titre')} ({paper.get('year', 'N/A')})",
            expanded=(i < 3)
        ):
            is_selected = st.checkbox("Inclure dans l'état de l'art", value=True, key=f"select_{i}")
            
            # Infos compactes
            authors = paper.get('authors', [])
            author_names = ', '.join([a.get('name', '') for a in authors[:3]])
            if len(authors) > 3:
                author_names += " et al."
            
            st.markdown(f"**Auteurs :** {author_names}")
            st.markdown(f"**Année :** {paper.get('year', 'N/A')} • **Citations :** {paper.get('citationCount', 0)}")
            
            if paper.get('url'):
                st.markdown(f"[Accéder à l'article]({paper['url']})")
            
            st.markdown("---")
            summary = paper.get('summary', 'Résumé non disponible')
            st.write(summary)
            
            # Section abstract manuel
            _display_manual_abstract_section(paper, i)
            
            if is_selected:
                selected_papers.append(paper)
    
    st.markdown(f"<p style='font-weight: 600; color: {COLOR_PRIMARY}; margin-top: 1rem;'>{len(selected_papers)} articles sélectionnés</p>", unsafe_allow_html=True)
    
    return selected_papers


def _display_manual_abstract_section(paper: Dict, index: int):
    """Section d'ajout manuel optimisée"""
    source_quality = paper.get('source_quality', '🔴')
    has_abstract = paper.get('abstract') and len(str(paper.get('abstract', '')).strip()) > 50
    
    if source_quality == '🔴' or not has_abstract:
        st.markdown("---")
        st.markdown("**Ajouter un résumé manuellement**")
        
        manual_abstract = st.text_area(
            "Abstract",
            value=paper.get('manual_abstract', ''),
            height=120,
            key=f"manual_abstract_{index}",
            placeholder="Collez l'abstract si vous l'avez trouvé..."
        )
        
        if st.button(f"Enregistrer", key=f"save_abstract_{index}"):
            if manual_abstract and len(manual_abstract.strip()) > 50:
                paper['manual_abstract'] = manual_abstract
                paper['abstract'] = manual_abstract
                paper['enrichment_source'] = 'manual'
                paper['source_quality'] = '🟡'
                st.success("Abstract enregistré")
                return True
            else:
                st.warning("L'abstract doit contenir au moins 50 caractères")
    
    return False

def _display_api_keys_section():
    """Affiche la section de configuration des clés API avec détection automatique"""
    import config_api
    
    st.markdown("**🔑 Clés API**")
    
    # ========================================
    # GEMINI API KEY (obligatoire)
    # ========================================
    gemini_in_config = (
        hasattr(config_api, 'GEMINI_API_KEY') and 
        config_api.GEMINI_API_KEY and 
        config_api.GEMINI_API_KEY != "VOTRE_CLE_GEMINI_ICI"
    )
    
    # Valeur par défaut : depuis config ou session_state
    default_gemini = config_api.GEMINI_API_KEY if gemini_in_config else st.session_state.get('gemini_api_key', '')
    
    # Afficher le champ avec indication si déjà configuré
    if gemini_in_config:
        st.markdown("<small style='color: #28a745;'>✓ Clé Gemini détectée dans config_api.py</small>", unsafe_allow_html=True)
    
    gemini_key = st.text_input(
        "Gemini API Key *",
        value=default_gemini,
        type="password",
        help="Obligatoire - https://makersuite.google.com/app/apikey",
        key="gemini_api_key_input",
        placeholder="Entrez votre clé Gemini ou laissez celle du fichier config"
    )
    
    if gemini_key:
        st.session_state.gemini_api_key = gemini_key
        if not gemini_in_config:
            st.markdown("<small style='color: #28a745;'>✓ Clé Gemini validée</small>", unsafe_allow_html=True)
    else:
        st.markdown("<small style='color: #dc3545;'>✗ Clé Gemini manquante</small>", unsafe_allow_html=True)
    
    # ========================================
    # CLÉS OPTIONNELLES
    # ========================================
    with st.expander("🔧 Clés optionnelles"):
        # Semantic Scholar
        semantic_in_config = (
            hasattr(config_api, 'SEMANTIC_SCHOLAR_API_KEY') and 
            config_api.SEMANTIC_SCHOLAR_API_KEY and 
            config_api.SEMANTIC_SCHOLAR_API_KEY != "VOTRE_CLE_SEMANTIC_SCHOLAR_ICI"
        )
        
        default_semantic = config_api.SEMANTIC_SCHOLAR_API_KEY if semantic_in_config else st.session_state.get('semantic_scholar_api_key', '')
        
        if semantic_in_config:
            st.markdown("<small style='color: #28a745;'>✓ Clé Semantic Scholar détectée dans config_api.py</small>", unsafe_allow_html=True)
        
        semantic_key = st.text_input(
            "Semantic Scholar API Key",
            value=default_semantic,
            type="password",
            help="Optionnel - Augmente les limites",
            key="semantic_scholar_api_key_input",
            placeholder="Entrez votre clé Semantic Scholar (optionnel)"
        )
        
        if semantic_key:
            st.session_state.semantic_scholar_api_key = semantic_key
            if not semantic_in_config:
                st.markdown("<small style='color: #28a745;'>✓ Clé Semantic Scholar validée</small>", unsafe_allow_html=True)
        else:
            st.markdown("<small style='color: #999;'>○ Semantic Scholar non configurée (optionnel)</small>", unsafe_allow_html=True)
        
        # CORE
        core_in_config = (
            hasattr(config_api, 'CORE_API_KEY') and 
            config_api.CORE_API_KEY and 
            config_api.CORE_API_KEY != "VOTRE_CLE_CORE_ICI"
        )
        
        default_core = config_api.CORE_API_KEY if core_in_config else st.session_state.get('core_api_key', '')
        
        if core_in_config:
            st.markdown("<small style='color: #28a745;'>✓ Clé CORE détectée dans config_api.py</small>", unsafe_allow_html=True)
        
        core_key = st.text_input(
            "CORE API Key",
            value=default_core,
            type="password",
            help="Optionnel - Meilleur enrichissement",
            key="core_api_key_input",
            placeholder="Entrez votre clé CORE (optionnel)"
        )
        
        if core_key:
            st.session_state.core_api_key = core_key
            if not core_in_config:
                st.markdown("<small style='color: #28a745;'>✓ Clé CORE validée</small>", unsafe_allow_html=True)
        else:
            st.markdown("<small style='color: #999;'>○ CORE non configurée (optionnel)</small>", unsafe_allow_html=True)
        
        st.caption("[Obtenir les clés optionnelles](https://www.semanticscholar.org/product/api)")