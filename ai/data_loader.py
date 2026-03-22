# ai/data_loader.py
import json
from pathlib import Path
from typing import List, Dict, Optional

def load_aceob_data(data_dir: str = "data/ACEOB/ACEOB", split: str = "train", sample_size: int = None) -> List[Dict[str, str]]:
    """
    Parcourt le dataset ACEOB pour charger les paires de code inefficace/efficace.
    Le dossier data_dir doit contenir des sous-dossiers 'train' et 'test'.
    """
    root = Path(data_dir) / split
    if not root.exists():
        raise FileNotFoundError(f"Dataset split {split} introuvable : {root}")

    pairs = []
    problem_dirs = [d for d in root.iterdir() if d.is_dir()]
    print(f"Problèmes trouvés dans {split} : {len(problem_dirs)}")

    for prob_dir in problem_dirs:
        # Chercher les sous-dossiers de paires
        pair_dirs = list(prob_dir.glob("Efficient-inefficient_code_pairs_*"))
        for pair_dir in pair_dirs:
            # Chercher les fichiers .txt
            files = list(pair_dir.glob("*.txt"))
            inefficient_file = None
            efficient_file = None
            for f in files:
                if "Inefficient" in f.name:
                    inefficient_file = f
                elif "Efficient" in f.name:
                    efficient_file = f
            if inefficient_file and efficient_file:
                try:
                    with open(inefficient_file, 'r', encoding='utf-8') as fin:
                        inefficient_code = fin.read()
                    with open(efficient_file, 'r', encoding='utf-8') as feff:
                        efficient_code = feff.read()
                    pairs.append({
                        "inefficient_code": inefficient_code,
                        "efficient_code": efficient_code,
                        "problem_id": prob_dir.name,
                        "pair_id": pair_dir.name
                    })
                except Exception as e:
                    print(f"Erreur lecture {pair_dir}: {e}")
                if sample_size and len(pairs) >= sample_size:
                    break
        if sample_size and len(pairs) >= sample_size:
            break

    print(f"Paires chargées dans {split} : {len(pairs)}")
    return pairs

def prepare_code_pairs(data: List[Dict]) -> tuple:
    """Extrait les listes de codes inefficaces et efficaces."""
    sources = [item['inefficient_code'] for item in data]
    targets = [item['efficient_code'] for item in data]
    return sources, targets

def inspect_sample(data: List[Dict], n: int = 3):
    """Affiche quelques exemples."""
    for i, item in enumerate(data[:n]):
        print(f"\n--- Exemple {i+1} ---")
        print(f"Problème ID : {item['problem_id']}")
        print(f"Pair ID : {item['pair_id']}")
        print("Code inefficace (début) :")
        print(item['inefficient_code'][:300])
        print("Code efficace (début) :")
        print(item['efficient_code'][:300])