# knowledge/storage.py
import json
import os
from knowledge.knowledge_base import PATTERNS, AlgorithmPattern

PATTERNS_FILE = os.path.join(os.path.dirname(__file__), "patterns.json")

def save_patterns():
    """Sauvegarde les patterns dans un fichier JSON."""
    data = []
    for p in PATTERNS:
        # On ne sauvegarde pas le détecteur (fonction)
        data.append({
            "name": p.name,
            "description": p.description,
            "suggestion": p.suggestion,
            "explanation": p.explanation,
            "source": p.source
        })
    with open(PATTERNS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_patterns():
    """Charge les patterns depuis le fichier JSON et les ajoute à PATTERNS."""
    global PATTERNS
    try:
        with open(PATTERNS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # On vide la liste existante pour éviter les doublons
        PATTERNS.clear()
        for item in data:
            # Créer un pattern avec un détecteur factice (à remplacer plus tard)
            pattern = AlgorithmPattern(
                name=item["name"],
                description=item["description"],
                detector=lambda func, source: False,  # prend deux arguments
                suggestion=item["suggestion"],
                explanation=item["explanation"],
                source=item["source"]
            )
            PATTERNS.append(pattern)
        print(f"Chargement de {len(PATTERNS)} motifs depuis {PATTERNS_FILE}")
    except FileNotFoundError:
        print("Aucun fichier de motifs trouvé, démarrage avec une base vide.")
    except Exception as e:
        print(f"Erreur lors du chargement des motifs : {e}")

