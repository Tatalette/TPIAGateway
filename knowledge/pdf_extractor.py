# knowledge/pdf_extractor.py
from unstructured.partition.auto import partition
from typing import List, Dict, Any

def extract_blocks(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extrait les blocs sémantiques d'un PDF.
    Retourne une liste de dict avec 'category' et 'text'.
    """
    elements = partition(filename=pdf_path)
    blocks = []
    for el in elements:
        blocks.append({
            "category": el.category,
            "text": el.text.strip()
        })
    return blocks

def filter_blocks(blocks: List[Dict], categories=None, keywords=None):
    """
    Filtre les blocs par catégorie et/ou mots-clés.
    """
    if categories:
        blocks = [b for b in blocks if b["category"] in categories]
    if keywords:
        # recherche insensible à la casse
        lower_keywords = [k.lower() for k in keywords]
        blocks = [b for b in blocks if any(k in b["text"].lower() for k in lower_keywords)]
    return blocks