# knowledge/knowledge_builder.py
from knowledge.knowledge_base import PATTERNS, AlgorithmPattern
from typing import List

def build_pattern_from_info(info: dict) -> AlgorithmPattern:
    """
    Construit un objet AlgorithmPattern à partir des infos NLP.
    (Version simplifiée, nécessite une validation humaine)
    """
    # On prend le premier nom d'entité comme nom d'algo, sinon "inconnu"
    algo_name = info["entities"][0] if info["entities"] else "algorithme"
    # On utilise les mots-clés pour générer une description
    description = f"Algorithme détecté : {', '.join(info['keywords'])}"
    # Suggestion générique
    suggestion = "Consultez la section correspondante dans le PDF pour optimiser."
    # Explication
    explanation = f"Le PDF mentionne {algo_name} avec des complexités {info['complexities']}."
    source = "PDF analysé"
    # Détecteur : pour l'instant on met un détecteur factice (toujours faux)
    # Plus tard, on pourrait essayer de générer un détecteur basé sur du code
    detector = lambda func: False  # à améliorer
    return AlgorithmPattern(
        name=algo_name,
        description=description,
        detector=detector,
        suggestion=suggestion,
        explanation=explanation,
        source=source
    )

def add_patterns_from_pdf(pdf_path: str):
    """
    Pipeline complet : extraction, NLP, création de patterns et ajout à la base.
    """
    from knowledge.pdf_extractor import extract_blocks
    from knowledge.nlp_extractor import extract_from_blocks

    blocks = extract_blocks(pdf_path)
    enriched = extract_from_blocks(blocks)
    new_patterns = []
    for info in enriched:
        pattern = build_pattern_from_info(info)
        new_patterns.append(pattern)
    # Ajout à la base (attention à ne pas dupliquer)
    for p in new_patterns:
        # Vérifier si un pattern avec le même nom existe déjà
        if not any(existing.name == p.name for existing in PATTERNS):
            PATTERNS.append(p)
    return new_patterns