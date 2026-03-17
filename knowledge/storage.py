# knowledge/storage.py
import json
from knowledge.knowledge_base import PATTERNS, AlgorithmPattern

PATTERNS_FILE = "patterns.json"

def save_patterns():
    data = []
    for p in PATTERNS:
        # On ne peut pas sérialiser la fonction detector (lambda)
        # On ne sauvegarde que les données descriptives
        data.append({
            "name": p.name,
            "description": p.description,
            "suggestion": p.suggestion,
            "explanation": p.explanation,
            "source": p.source
            # on ne sauvegarde pas le détecteur
        })
    with open(PATTERNS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_patterns():
    try:
        with open(PATTERNS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            # recréer un pattern avec un détecteur factice (à remplacer par une vraie logique plus tard)
            pattern = AlgorithmPattern(
                name=item["name"],
                description=item["description"],
                detector=lambda func: False,  # par défaut, ne détecte rien
                suggestion=item["suggestion"],
                explanation=item["explanation"],
                source=item["source"]
            )
            PATTERNS.append(pattern)
    except FileNotFoundError:
        pass