"""
Configuration des clés API et constantes
"""

# Clés API - REMPLACEZ PAR VOS VRAIES CLÉS
GEMINI_API_KEY = "VOTRE_CLE_GEMINI_ICI"  
SEMANTIC_SCHOLAR_API_KEY = "VOTRE_CLE_SEMANTIC_SCHOLAR_ICI" 
CORE_API_KEY = "VOTRE_CLE_CORE_ICI"

# Timeouts (en secondes)
ENRICHMENT_TIMEOUT = 180  # 3 minutes pour l'enrichissement
GLOBAL_TIMEOUT = 210      # 3'30 timeout global
ARTICLE_TIMEOUT = 30      # 10 secondes max par article

# Fichier d'historique
HISTORY_FILE = "search_history.json"

# Configuration Semantic Scholar
SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/graph/v1"

# Modèles LLM disponibles
GEMINI_MODELS = [
    "models/gemini-2.5-flash",
    "models/gemini-2.5-pro"
]

# Paramètres par défaut
DEFAULT_MAX_ARTICLES = 15
DEFAULT_GEMINI_MODEL = "models/gemini-2.5-flash"

class Config:
    """Configuration centralisée pour faciliter le changement de LLM"""
    semantic_scholar_api_url: str = "https://api.semanticscholar.org/graph/v1"
    max_articles: int = 15  # Augmenté pour gérer 3 stratégies
    llm_provider: str = "gemini"
    gemini_model: str = "gemini-2.5-flash"
    
    # NOUVEAU : Paramètres par stratégie
    strategy_configs: dict = None
    
    def __post_init__(self):
        if self.strategy_configs is None:
            self.strategy_configs = {
                'fundamental': {
                    'max_articles': 12,
                    'queries_per_subproblem': 1,  # Recherche précise
                    'subproblems_count': 4
                },
                'applied': {
                    'max_articles': 12,
                    'queries_per_subproblem': 2,  # Recherche élargie
                    'subproblems_count': 4
                },
                'experimental': {
                    'max_articles': 12,
                    'queries_per_subproblem': 3,  # Recherche très large + décomposition
                    'subproblems_count': 4
                }
            }    
            
    #Configuration des stratégies
    def get_strategy_config(self, strategy: str) -> dict:
        """Retourne la config pour une stratégie donnée"""
        configs = {
            'fundamental': {
                'max_articles': 12,
                'num_queries': 1,
                'keywords_count': 5
            },
            'applied': {
                'max_articles': 12,
                'num_queries': 2,
                'keywords_count': 8
            },
            'experimental': {
                'max_articles': 12,
                'num_queries': 3,
                'keywords_count': 12
            }
        }
        return configs.get(strategy, configs['experimental'])