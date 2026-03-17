# knowledge/knowledge_builder.py
from knowledge.knowledge_base import PATTERNS, AlgorithmPattern
from knowledge.storage import save_patterns
from typing import List
from knowledge.nlp_extractor import extract_from_blocks
from knowledge.nlp_extractor import ALGO_KEYWORDS

def build_pattern_from_info(info: dict) -> AlgorithmPattern:
    """Construit un objet AlgorithmPattern à partir des infos NLP, avec un nom plus pertinent."""
    
    # Stratégie de choix du nom :
    # 1. Si une entité ressemble à un nom d'algo (ex: "tri rapide", "quicksort"), on la prend.
    # 2. Sinon, si des complexités sont présentes, on génère un nom basé sur les mots-clés.
    # 3. Sinon, on utilise le premier mot-clé.
    # 4. En dernier recours, on ignore le bloc (retour None).
    
    name = None
    if info["entities"]:
        # Prendre la première entité qui contient au moins un mot technique
        for ent in info["entities"]:
            if any(kw in ent.lower() for kw in ALGO_KEYWORDS):
                name = ent
                break
        if not name:
            name = info["entities"][0]  # fallback
    if not name and info["keywords"]:
        name = info["keywords"][0].capitalize() + "_algo"
    if not name:
        # Bloc jugé non pertinent
        return None
    
    description = f"Algorithme détecté : {', '.join(info['keywords'])}"
    suggestion = "Consultez la section correspondante dans le PDF pour optimiser votre code."
    explanation = f"Le PDF mentionne {name} avec des complexités {info['complexities']}."
    source = "PDF analysé"
    detector = lambda func: False  # factice pour l'instant
    return AlgorithmPattern(
        name=name,
        description=description,
        detector=detector,
        suggestion=suggestion,
        explanation=explanation,
        source=source
    )


def add_patterns_from_pdf(pdf_path: str) -> List[AlgorithmPattern]:
    """
    Pipeline complet : extraction, NLP, création de patterns et ajout à la base.
    """
    from knowledge.pdf_extractor import extract_blocks
    from knowledge.nlp_extractor import extract_from_blocks

    print(f"Extraction du PDF : {pdf_path}")
    blocks = extract_blocks(pdf_path)
    print(f"Nombre de blocs extraits : {len(blocks)}")

    enriched = extract_from_blocks(blocks)
    print(f"Blocs enrichis : {len(enriched)}")

    new_patterns = []
    for info in enriched:
        pattern = build_pattern_from_info(info)
        if pattern is None:
            continue
        # Vérification doublon (sur le nom)
        if not any(p.name == pattern.name for p in PATTERNS):
            PATTERNS.append(pattern)
            new_patterns.append(pattern)
            print(f"Ajout du motif : {pattern.name}")
        else:
            print(f"Motif déjà existant : {pattern.name}")

    if new_patterns:
        save_patterns()
        print(f"{len(new_patterns)} nouveau(x) motif(s) sauvegardé(s).")
    else:
        print("Aucun nouveau motif détecté.")

    return new_patterns
