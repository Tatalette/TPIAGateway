# knowledge/nlp_extractor.py
import spacy
from typing import List, Dict, Any

# Charger le modèle de langue (à adapter selon la langue des PDF)
nlp = spacy.load("fr_core_news_sm")  # ou "en_core_web_sm"

# Liste de mots-clés pour détecter une description d'algorithme
ALGO_KEYWORDS = ["algorithme", "tri", "recherche", "parcours", "dichotomique", "bulles", "rapide", "fusion", "insertion", "complexité", "optimisation", "performance"]

def extract_algorithm_info(text: str) -> Dict[str, Any]:
    """
    Analyse un texte et retourne les informations algorithmiques potentielles.
    """
    doc = nlp(text)
    # Extraction des entités nommées
    entities = [ent.text for ent in doc.ents if ent.label_ in ("MISC", "TECH", "ALGO")]  # adapter selon le modèle
    # Extraction des notations de complexité (pattern regex simple)
    import re
    complexity_pattern = r'O\s*\(\s*[nNlLgk\^ \d]+\s*\)'
    complexities = re.findall(complexity_pattern, text, re.IGNORECASE)
    # Détection de mots-clés
    keywords_found = [kw for kw in ALGO_KEYWORDS if kw.lower() in text.lower()]
    return {
        "entities": entities,
        "complexities": complexities,
        "keywords": keywords_found,
        "text_snippet": text[:500]  # pour référence
    }

def extract_from_blocks(blocks: List[Dict]) -> List[Dict]:
    """
    Applique l'analyse NLP à chaque bloc et retourne les blocs enrichis.
    """
    enriched = []
    for block in blocks:
        info = extract_algorithm_info(block["text"])
        if info["entities"] or info["complexities"] or info["keywords"]:
            block.update(info)
            enriched.append(block)
    return enriched