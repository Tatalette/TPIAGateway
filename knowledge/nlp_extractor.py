# knowledge/nlp_extractor.py
import spacy
import re
from typing import List, Dict, Any

# Charger le modèle de langue
try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    print("Modèle spaCy non trouvé. Installez-le avec: python -m spacy download fr_core_news_sm")
    nlp = None

# Mots-clés pour détecter un algorithme
ALGO_KEYWORDS = [
    "algorithme", "tri", "recherche", "parcours", "dichotomique", 
    "bulles", "rapide", "fusion", "insertion", "complexité", 
    "optimisation", "performance", "récursif", "itératif",
    "diviser pour régner", "programmation dynamique", "glouton"
]

# Noms d'algorithmes courants (pour reconnaissance)
ALGO_NAMES = [
    "tri bulles", "tri à bulles", "bubble sort",
    "tri rapide", "quicksort", "quick sort",
    "tri fusion", "merge sort",
    "tri insertion", "insertion sort",
    "recherche dichotomique", "binary search",
    "recherche linéaire", "linear search",
    "dijkstra", "bellman-ford", "kruskal", "prim",
    "programmation dynamique", "dynamic programming"
]

def extract_algorithm_info(text: str) -> Dict[str, Any]:
    """
    Analyse un texte et retourne les informations algorithmiques potentielles,
    avec un score de confiance.
    """
    lower_text = text.lower()
    entities = []
    if nlp:
        doc = nlp(text)
        entities = [ent.text for ent in doc.ents if ent.label_ in ("MISC", "TECH", "PRODUCT")]
    
    # Extraction des complexités
    complexity_pattern = r'O\s*\([^)]+\)'
    complexities = re.findall(complexity_pattern, text, re.IGNORECASE)
    
    # Mots-clés trouvés
    keywords_found = [kw for kw in ALGO_KEYWORDS if kw.lower() in lower_text]
    
    # Noms d'algorithmes trouvés (on cherche des phrases complètes)
    algo_names_found = []
    for name in ALGO_NAMES:
        if name.lower() in lower_text:
            algo_names_found.append(name)
    
    # Calcul d'un score de pertinence
    score = len(keywords_found) * 2 + len(complexities) * 3 + len(algo_names_found) * 5 + len(entities)
    
    return {
        "entities": entities,
        "complexities": complexities,
        "keywords": keywords_found,
        "algo_names": algo_names_found,
        "score": score,
        "text_snippet": text[:300]
    }

def extract_from_blocks(blocks: List[Dict], min_score: int = 5) -> List[Dict]:
    """
    Applique l'analyse NLP à chaque bloc et retourne les blocs enrichis
    ayant un score supérieur à min_score.
    """
    enriched = []
    for block in blocks:
        info = extract_algorithm_info(block["text"])
        if info["score"] >= min_score:
            block.update(info)
            enriched.append(block)
    return enriched

# knowledge/nlp_extractor.py (extrait modifié)

# Liste de mots-clés techniques pour renforcer la pertinence
TECH_KEYWORDS = [
    "algorithme", "tri", "recherche", "complexité", "optimisation",
    "récursif", "itératif", "complexité", "performance", "dichotomique",
    "bulles", "rapide", "fusion", "insertion", "dichotomique", "binaire",
    "pile", "file", "graphe", "arbre", "parcours", "profondeur", "largeur",
    "dijkstra", "bellman", "ford", "kruskal", "prim", "floyd", "warshall"
]

def is_relevant_block(text: str) -> bool:
    """
    Détermine si un bloc de texte est susceptible de contenir une description algorithmique.
    """
    text_lower = text.lower()
    # Au moins un mot-clé technique
    if not any(kw in text_lower for kw in TECH_KEYWORDS):
        return False
    # Longueur minimale (éviter les fragments trop courts)
    if len(text) < 20:
        return False
    # Éviter les blocs avec trop de formules mathématiques (ex: trop de symboles)
    # (Optionnel) On peut compter la proportion de caractères spéciaux
    return True

def extract_algorithm_info(text: str) -> Dict[str, Any]:
    """Version améliorée avec filtrage."""
    if not is_relevant_block(text):
        return {"entities": [], "complexities": [], "keywords": [], "text_snippet": ""}
    
    entities = []
    if nlp:
        doc = nlp(text)
        # On garde les entités de type 'MISC' ou 'TECH' (selon le modèle) et on filtre les trop courtes
        entities = [
            ent.text for ent in doc.ents 
            if ent.label_ in ("MISC", "TECH", "PRODUCT") and len(ent.text) > 2
        ]
    
    complexities = re.findall(r'O\s*\([^)]+\)', text, re.IGNORECASE)
    
    keywords_found = [kw for kw in ALGO_KEYWORDS if kw.lower() in text.lower()]
    
    return {
        "entities": entities,
        "complexities": complexities,
        "keywords": keywords_found,
        "text_snippet": text[:500]
    }

def extract_from_blocks(blocks: List[Dict]) -> List[Dict]:
    enriched = []
    for block in blocks:
        info = extract_algorithm_info(block["text"])
        if info["entities"] or info["complexities"] or info["keywords"]:
            block.update(info)
            enriched.append(block)
    return enriched