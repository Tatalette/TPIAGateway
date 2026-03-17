# knowledge/nlp_extractor.py
import spacy
import re
from typing import List, Dict, Any

# Charger le modèle de langue (à adapter selon la langue des PDF)
try:
    nlp = spacy.load("fr_core_news_sm")  # ou "en_core_web_sm"
except OSError:
    print("Modèle spaCy non trouvé. Installez-le avec: python -m spacy download fr_core_news_sm")
    nlp = None

ALGO_KEYWORDS = [
    "algorithme", "tri", "recherche", "parcours", "dichotomique", 
    "bulles", "rapide", "fusion", "insertion", "complexité", 
    "optimisation", "performance"
]

def extract_algorithm_info(text: str) -> Dict[str, Any]:
    """
    Analyse un texte et retourne les informations algorithmiques potentielles.
    """
    entities = []
    if nlp:
        doc = nlp(text)
        entities = [ent.text for ent in doc.ents if ent.label_ in ("MISC", "TECH", "PRODUCT")]
    
    # Extraction des notations de complexité (pattern amélioré)
    complexity_pattern = r'O\s*\([^)]+\)'
    complexities = re.findall(complexity_pattern, text, re.IGNORECASE)
    
    keywords_found = [kw for kw in ALGO_KEYWORDS if kw.lower() in text.lower()]
    
    return {
        "entities": entities,
        "complexities": complexities,
        "keywords": keywords_found,
        "text_snippet": text[:500]
    }