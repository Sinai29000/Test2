"""
Enrichissement des articles via Unpaywall, ArXiv et CORE
"""

import requests
import time
import fitz  # PyMuPDF
from io import BytesIO
from typing import Dict, Optional
from config_api import ARTICLE_TIMEOUT


class ArticleEnricher:
    """Enrichit les articles avec du contenu supplémentaire"""
    
    def __init__(self, email: str = "user@example.com", core_api_key: str = None):
        self.email = email
        self.core_api_key = core_api_key
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Scientific-Review-Generator/1.0'})
    
    def get_unpaywall_pdf(self, doi: str) -> Optional[str]:
        """Récupère l'URL du PDF via Unpaywall si disponible"""
        if not doi:
            return None
        
        try:
            url = f"https://api.unpaywall.org/v2/{doi}?email={self.email}"
            print(f"   📡 Requête Unpaywall: {url}")
            response = self.session.get(url, timeout=5)
            
            print(f"   📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                is_oa = data.get('is_oa', False)
                print(f"   📖 Open Access: {is_oa}")
                
                if is_oa and data.get('best_oa_location'):
                    pdf_url = data['best_oa_location'].get('url_for_pdf')
                    if pdf_url:
                        print(f"   ✅ PDF URL trouvée: {pdf_url[:50]}...")
                        return pdf_url
                    else:
                        print(f"   ⚠️ Open Access mais pas de PDF URL")
                else:
                    print(f"   ⚠️ Article pas en open access")
            else:
                print(f"   ❌ Erreur HTTP: {response.status_code}")
            
        except Exception as e:
            print(f"   ❌ Exception Unpaywall: {str(e)}")
        
        return None
    
    def get_arxiv_abstract(self, arxiv_id: str) -> Optional[str]:
        """Récupère l'abstract complet depuis ArXiv"""
        if not arxiv_id:
            return None
        
        try:
            arxiv_id = arxiv_id.replace('arXiv:', '').strip()
            url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                entry = root.find('atom:entry', ns)
                
                if entry is not None:
                    summary = entry.find('atom:summary', ns)
                    if summary is not None:
                        return summary.text.strip()
        except Exception as e:
            print(f"Erreur ArXiv pour ID {arxiv_id}: {e}")
        
        return None
    
    def extract_text_from_pdf(self, pdf_url: str, max_chars: int = 2000) -> Optional[str]:
        """Extrait le texte des premières pages d'un PDF"""
        try:
            response = self.session.get(pdf_url, timeout=10, stream=True)
            
            if response.status_code == 200:
                pdf_data = BytesIO(response.content)
                doc = fitz.open(stream=pdf_data, filetype="pdf")
                
                text = ""
                for page_num in range(min(2, len(doc))):
                    page = doc[page_num]
                    text += page.get_text()
                    
                    if len(text) >= max_chars:
                        break
                
                doc.close()
                
                text_lower = text.lower()
                if 'abstract' in text_lower:
                    abstract_start = text_lower.find('abstract')
                    relevant_text = text[abstract_start:abstract_start + max_chars]
                    return relevant_text
                
                return text[:max_chars]
        
        except Exception as e:
            print(f"Erreur extraction PDF {pdf_url}: {e}")
        
        return None
    
    def get_core_abstract(self, doi: str, title: str = None) -> Optional[str]:
        """Récupère l'abstract depuis CORE API"""
        if not self.core_api_key:
            return None
        
        # Stratégie 1 : Recherche par DOI
        if doi:
            try:
                url = "https://api.core.ac.uk/v3/search/works"
                headers = {'Authorization': f'Bearer {self.core_api_key}'}
                params = {'q': f'doi:"{doi}"', 'limit': 1}
                
                print(f"   🔍 Tentative CORE par DOI: {doi}")
                response = self.session.get(url, headers=headers, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    if results and len(results) > 0:
                        result = results[0]
                        abstract = result.get('abstract', '') or result.get('description', '')
                        
                        if abstract and len(abstract) > 50:
                            print(f"   ✅ Abstract CORE trouvé (DOI) ! Longueur: {len(abstract)}")
                            return abstract
                    else:
                        print(f"   ⚠️ Pas de résultat CORE pour ce DOI")
                else:
                    print(f"   ⚠️ CORE erreur: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Erreur CORE (DOI): {str(e)}")
        
        # Stratégie 2 : Recherche par titre
        if title and len(title) > 10:
            try:
                url = "https://api.core.ac.uk/v3/search/works"
                headers = {'Authorization': f'Bearer {self.core_api_key}'}
                clean_title = title.replace('"', '').strip()[:100]
                params = {'q': f'title:"{clean_title}"', 'limit': 1}
                
                print(f"   🔍 Tentative CORE par titre")
                response = self.session.get(url, headers=headers, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    if results and len(results) > 0:
                        result = results[0]
                        abstract = result.get('abstract', '') or result.get('description', '')
                        
                        if abstract and len(abstract) > 50:
                            print(f"   ✅ Abstract CORE trouvé (titre) ! Longueur: {len(abstract)}")
                            return abstract
                
            except Exception as e:
                print(f"   ❌ Erreur CORE (titre): {str(e)}")
        
        return None
    
    def enrich_paper(self, paper: Dict, timeout_start: float, max_time: float) -> Dict:
        """Enrichit un article avec du contenu supplémentaire"""
        if time.time() - timeout_start > max_time:
            paper['enrichment_status'] = 'timeout'
            paper['source_quality'] = '🔴'
            return paper
        
        article_start = time.time()
        title = paper.get('title', 'Sans titre')[:50]
        
        # Si abstract déjà présent
        if paper.get('abstract') and len(str(paper['abstract']).strip()) > 100:
            print(f"✅ Abstract déjà présent pour: {title}")
            paper['enrichment_status'] = 'complete'
            paper['source_quality'] = '🟢'
            return paper
        
        external_ids = paper.get('externalIds', {})
        doi = external_ids.get('DOI') if external_ids else None
        arxiv_id = external_ids.get('ArXiv') if external_ids else None
        
        enriched_content = None
        source = None
        
        # STRATÉGIE 1 : ArXiv
        if arxiv_id and time.time() - article_start < ARTICLE_TIMEOUT:
            print(f"🔍 Tentative ArXiv pour ID: {arxiv_id}")
            arxiv_abstract = self.get_arxiv_abstract(arxiv_id)
            if arxiv_abstract and len(arxiv_abstract) > 100:
                print(f"   ✅ ArXiv trouvé ! Longueur: {len(arxiv_abstract)}")
                enriched_content = arxiv_abstract
                source = 'arxiv'
                paper['enrichment_status'] = 'complete'
                paper['source_quality'] = '🟢'
        
        # STRATÉGIE 2 : TLDR
        if not enriched_content and paper.get('tldr') and paper['tldr'].get('text'):
            tldr_text = paper['tldr']['text']
            if len(tldr_text) > 50:
                print(f"   ✅ TLDR trouvé ! Longueur: {len(tldr_text)}")
                enriched_content = tldr_text
                source = 'tldr'
                paper['enrichment_status'] = 'partial'
                paper['source_quality'] = '🟡'
        
        # STRATÉGIE 3 : CORE API
        if not enriched_content and self.core_api_key:
            title_full = paper.get('title', '')
            core_abstract = self.get_core_abstract(doi, title_full)
            if core_abstract and len(core_abstract) > 50:
                enriched_content = core_abstract
                source = 'core'
                paper['enrichment_status'] = 'partial'
                paper['source_quality'] = '🟡'
        
        # STRATÉGIE 4 : Unpaywall
        if not enriched_content and doi and time.time() - article_start < ARTICLE_TIMEOUT:
            print(f"🔍 Tentative Unpaywall pour DOI: {doi}")
            pdf_url = self.get_unpaywall_pdf(doi)
            if pdf_url:
                print(f"   🔍 Extraction du PDF...")
                pdf_text = self.extract_text_from_pdf(pdf_url)
                if pdf_text and len(pdf_text) > 100:
                    print(f"   ✅ PDF extrait ! Longueur: {len(pdf_text)}")
                    enriched_content = pdf_text
                    source = 'unpaywall_pdf'
                    paper['enrichment_status'] = 'partial'
                    paper['source_quality'] = '🟡'
        
        # STRATÉGIE 5 : OpenAccessPdf
        if not enriched_content and paper.get('openAccessPdf') and paper['openAccessPdf'].get('url'):
            pdf_url = paper['openAccessPdf']['url']
            print(f"   🔍 Tentative PDF Semantic Scholar")
            if time.time() - article_start < ARTICLE_TIMEOUT:
                pdf_text = self.extract_text_from_pdf(pdf_url)
                if pdf_text and len(pdf_text) > 100:
                    print(f"   ✅ PDF Semantic Scholar extrait ! Longueur: {len(pdf_text)}")
                    enriched_content = pdf_text
                    source = 'semantic_scholar_pdf'
                    paper['enrichment_status'] = 'partial'
                    paper['source_quality'] = '🟡'
        
        # Mettre à jour le paper
        if enriched_content:
            paper['abstract'] = enriched_content
            paper['enrichment_source'] = source
            print(f"✅ Article enrichi ! Source: {source}, Longueur: {len(enriched_content)}")
        else:
            paper['enrichment_status'] = 'failed'
            paper['source_quality'] = '🔴'
            print(f"❌ Échec enrichissement pour: {title}")
            
            reasons = []
            if not doi and not arxiv_id:
                reasons.append("Pas de DOI ni ArXiv ID")
            elif doi and not arxiv_id:
                reasons.append("Pas en open access")
            if not paper.get('tldr'):
                reasons.append("Pas de TLDR")
            if not self.core_api_key:
                reasons.append("CORE non configuré")
            if reasons:
                print(f"   ℹ️ Raisons: {', '.join(reasons)}")
        
        return paper