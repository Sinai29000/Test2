"""
Gestion de l'historique des recherches
"""

import json
import os
from typing import List
from config_api import HISTORY_FILE


def load_search_history() -> List[str]:
    """Charge l'historique des recherches depuis le fichier"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
                return history if isinstance(history, list) else []
    except Exception as e:
        print(f"Erreur lors du chargement de l'historique: {e}")
    return []


def save_search_history(history: List[str]):
    """Sauvegarde l'historique des recherches dans le fichier"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de l'historique: {e}")


def add_to_history(question: str, history: List[str]) -> List[str]:
    """Ajoute une question à l'historique (évite les doublons)"""
    # Retirer la question si elle existe déjà
    if question in history:
        history.remove(question)
    
    # Ajouter la question au début
    history.insert(0, question)
    
    # Limiter à 20 recherches
    if len(history) > 20:
        history = history[:20]
    
    # Sauvegarder
    save_search_history(history)
    
    return history