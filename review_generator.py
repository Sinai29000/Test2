"""
Génération des résumés et de l'état de l'art
"""

import streamlit as st
from typing import Dict, List


class ReviewGenerator:
    """Génère l'état de l'art à partir des articles sélectionnés"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def summarize_paper(self, paper: Dict) -> str:
        """
        Génère un résumé complet d'un article pour la liste de validation.
        Utilise l'abstract enrichi si disponible.
        """
        title = paper.get('title', 'Sans titre')
        abstract = paper.get('abstract', None)
        year = paper.get('year', 'N/A')
        authors_list = paper.get('authors', [])
        authors = ', '.join([a.get('name', '') for a in authors_list[:3]])
        if len(authors_list) > 3:
            authors += " et al."
        citations = paper.get('citationCount', 0)
        source_quality = paper.get('source_quality', '🔴')
        enrichment_source = paper.get('enrichment_source', None)
        
        # 1. Si abstract disponible (original ou enrichi), générer un résumé détaillé
        if abstract and len(str(abstract).strip()) > 50:
            prompt = f"""
            Génère un résumé détaillé et complet de cet article scientifique en français (5-7 phrases).
            Le résumé doit couvrir:
            - Le contexte et la problématique
            - La méthodologie utilisée
            - Les principaux résultats
            - Les contributions/conclusions principales
            
            Titre: {title}
            Auteurs: {authors}
            Année: {year}
            Citations: {citations}
            
            Abstract complet: {abstract}
            
            Rédige un résumé substantiel et informatif en français.
            """
            
            try:
                summary = self.llm.generate(prompt, temperature=0.3)
                if summary and summary.strip() and len(summary.strip()) > 100:
                    # Ajouter l'indicateur de qualité
                    quality_labels = {
                        '🟢': '**Abstract original complet**',
                        '🟡': '**Contenu enrichi** (PDF/ArXiv/TLDR)',
                        '🔴': '**Résumé limité**'
                    }
                    quality_label = quality_labels.get(source_quality, '')
                    
                    # Indiquer la source d'enrichissement si disponible
                    source_info = ""
                    if enrichment_source == 'arxiv':
                        source_info = " via ArXiv"
                    elif enrichment_source == 'unpaywall_pdf':
                        source_info = " via Unpaywall PDF"
                    elif enrichment_source == 'tldr':
                        source_info = " via TLDR"
                    elif enrichment_source == 'core':
                        source_info = " via CORE"
                    elif enrichment_source == 'manual':
                        source_info = " (ajouté manuellement)"
                    
                    return f"{source_quality} {quality_label}{source_info}\n\n{summary}"
            except Exception as e:
                print(f"Erreur génération résumé: {e}")
            
            # Fallback : retourne l'abstract tronqué
            return f"{source_quality} **Résumé original:**\n\n{str(abstract)[:500]}..."
        
        # 2. Si aucun contenu disponible
        paper_url = paper.get('url', '')
        external_ids = paper.get('externalIds', {})
        doi = external_ids.get('DOI', '') if external_ids else ''
        
        links = []
        if paper_url:
            links.append(f"[Semantic Scholar]({paper_url})")
        if doi:
            links.append(f"[DOI](https://doi.org/{doi})")
        
        link_text = " | ".join(links) if links else "Aucun lien disponible"
        
        return f"🔴 **Résumé non disponible**\n\n**Consultez l'article:** {link_text}\n\n**Titre:** {title}\n**Auteurs:** {authors} ({year})"
    
    def generate_full_review(self, papers: List[Dict], question: str) -> str:
        """
        Génère l'état de l'art complet (environ 2 pages).
        Structure: Introduction, Travaux existants, Limitations, Perspectives.
        """
        # Prépare les informations sur les articles
        papers_info = []
        for i, paper in enumerate(papers, 1):
            authors_list = paper.get('authors', [])
            authors = ', '.join([a.get('name', '') for a in authors_list[:3]])
            if len(authors_list) > 3:
                authors += " et al."
            
            # Utilise l'abstract, ou le TLDR, ou le summary généré
            abstract = paper.get('abstract', None)
            if abstract and abstract.strip():
                abstract_text = abstract[:800]
            elif paper.get('tldr') and paper.get('tldr').get('text'):
                abstract_text = paper['tldr']['text']
            else:
                # Utilise le summary qui a été généré par summarize_paper
                abstract_text = paper.get('summary', 'Non disponible')[:800]
            
            info = f"""
            Article {i}:
            - Titre: {paper.get('title', 'N/A')}
            - Auteurs: {authors}
            - Année: {paper.get('year', 'N/A')}
            - Citations: {paper.get('citationCount', 0)}
            - Résumé: {abstract_text}
            """
            papers_info.append(info)
        
        papers_text = "\n\n".join(papers_info)
        
        prompt = f"""
        Tu es un chercheur expert. Rédige un état de l'art scientifique complet et structuré 
        en français sur la question suivante: "{question}"
        
        Utilise les articles scientifiques ci-dessous comme base.
        
        {papers_text}
        
        Structure ton état de l'art en QUATRE sections obligatoires:
        
        1. INTRODUCTION (1 paragraphe)
           - Contextualise la problématique
           - Explique l'importance du sujet
        
        2. TRAVAUX EXISTANTS (60% du contenu)
           - Présente les contributions majeures de chaque article
           - Organise par thèmes ou approches
           - Cite les auteurs et années entre parenthèses
           - Compare les méthodes et résultats
        
        3. LIMITATIONS (20% du contenu)
           - Identifie les limites des approches actuelles
           - Points non résolus dans la littérature
           - Contradictions ou débats
        
        4. PERSPECTIVES ET AXES DE RECHERCHE (20% du contenu)
           - Directions futures prometteuses
           - Questions ouvertes
           - Recommandations pour de futurs travaux
           - Fais un lien avec la nécessité d'engager des travaux de recherche
        
        CONSIGNES:
        - Longueur: Environ 3 pages (1800 - 2000 mots).
        - Style: académique mais accessible
        - Synthèse: regroupe les travaux similaires
        - Citations: mentionne auteurs et années au format APA
        - Objectivité: présente les forces ET faiblesses
        
        Rédige maintenant l'état de l'art complet.
        """
        
        review = self.llm.generate(prompt, temperature=0.2)
        
        # Vérification de la génération
        if not review or review.strip() == "":
            st.error("⚠️ La génération de l'état de l'art a échoué")
            return "Erreur lors de la génération. Veuillez réessayer ou changer de modèle LLM."
        
        return review