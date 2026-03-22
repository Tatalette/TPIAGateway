#!/usr/bin/env python3
# cli/main.py
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

from core.parser import CodeParser
from core.style_checker import StyleChecker
from core.error_detector import PylintErrorDetector
from knowledge.algorithm_advisor import AlgorithmAdvisor
from knowledge.storage import load_patterns, save_patterns
from knowledge.knowledge_builder import add_patterns_from_pdf

# Import de l'indexeur ACEOB
try:
    from ai.optimized_indexer import CodeOptimizationIndexer
    INDEXER_AVAILABLE = True
except ImportError:
    INDEXER_AVAILABLE = False
    print("Indexeur optimisé non disponible.", file=sys.stderr)

DEFAULT_CONFIG = {
    "style": {
        "snake_case": True,
        "camel_case": True,
        "trailing_whitespace": True,
        "quotes": True
    },
    "pylint": {
        "enabled": True,
        "ignore": []
    },
    "algorithm": {
        "enabled": True,
        "keywords_threshold": 1
    }
}

def load_config(config_path: str = "config.yaml") -> Dict:
    config = DEFAULT_CONFIG.copy()
    if not Path(config_path).exists():
        return config
    if yaml is None:
        print("Avertissement: pyyaml n'est pas installé. Utilisation de la configuration par défaut.", file=sys.stderr)
        return config
    try:
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
        if user_config:
            for key, value in user_config.items():
                if key in config:
                    if isinstance(config[key], dict):
                        config[key].update(value)
                    else:
                        config[key] = value
                else:
                    config[key] = value
    except Exception as e:
        print(f"Erreur lors du chargement de la config: {e}", file=sys.stderr)
    return config

def collect_py_files(paths: List[str], recursive: bool) -> List[Path]:
    py_files = []
    for p in paths:
        path = Path(p)
        if path.is_file() and path.suffix == '.py':
            py_files.append(path)
        elif path.is_dir() and recursive:
            py_files.extend(path.rglob('*.py'))
        elif path.is_dir() and not recursive:
            print(f"Ignorer le dossier {p} (utilisez --recursive pour l'analyser)", file=sys.stderr)
        elif not path.exists():
            print(f"Fichier ou dossier introuvable: {p}", file=sys.stderr)
    return py_files

def analyze_file(filepath: Path, config: Dict, no_pylint: bool, no_algorithm: bool) -> List[Dict]:
    try:
        parser = CodeParser(str(filepath))
    except FileNotFoundError:
        return [{'line': 0, 'type': 'error', 'message': f"Fichier introuvable: {filepath}"}]
    except Exception as e:
        return [{'line': 0, 'type': 'error', 'message': f"Erreur de parsing: {e}"}]

    issues = []

    # Style
    style_checker = StyleChecker(parser)
    style_issues = style_checker.check_all()
    for issue in style_issues:
        issues.append(issue.to_dict())

    # Pylint
    if not no_pylint and config.get("pylint", {}).get("enabled", True):
        pylint_detector = PylintErrorDetector(parser)
        pylint_issues = pylint_detector.check()
        ignore_codes = set(config.get("pylint", {}).get("ignore", []))
        for issue in pylint_issues:
            if issue.type == 'pylint' and issue.extra.get('symbol') in ignore_codes:
                continue
            issues.append(issue.to_dict())

    # Algorithm
    if not no_algorithm and config.get("algorithm", {}).get("enabled", True):
        algo_advisor = AlgorithmAdvisor(parser)
        algo_issues = algo_advisor.analyze()
        issues.extend([issue.to_dict() for issue in algo_issues])

    return issues

def output_console(results: List[Dict[str, Any]]):
    total_issues = 0
    for result in results:
        file_issues = result['issues']
        if not file_issues:
            continue
        total_issues += len(file_issues)
        print(f"\n{result['file']}: {len(file_issues)} problème(s)")
        for issue in file_issues:
            line_info = f"ligne {issue['line']}" if issue.get('line') else "fichier"
            print(f"  - {line_info} : {issue['message']}")
            if 'suggestion' in issue and issue['suggestion']:
                print(f"    Suggestion : {issue['suggestion']}")
            if 'explanation' in issue:
                print(f"    Explication : {issue['explanation']}")
    print(f"\nTotal : {total_issues} problème(s) détecté(s)")

def output_json(results: List[Dict[str, Any]], output_file: Optional[str]):
    data = {
        "summary": {
            "total_files": len(results),
            "total_issues": sum(len(r['issues']) for r in results)
        },
        "files": results
    }
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_str)
    else:
        print(json_str)

def main():
    # Charger la configuration
    config = load_config()

    # Charger les motifs persistants
    load_patterns()

    parser = argparse.ArgumentParser(description="Revue de code Python")
    parser.add_argument("paths", nargs="+", help="Fichiers ou dossiers Python à analyser")
    parser.add_argument("--recursive", action="store_true", help="Analyser récursivement les sous-dossiers")
    parser.add_argument("--output", choices=["console", "json"], default="console", help="Format de sortie")
    parser.add_argument("--output-file", help="Fichier de sortie (pour JSON)")
    parser.add_argument("--no-pylint", action="store_true", help="Désactiver l'analyse pylint")
    parser.add_argument("--no-algorithm", action="store_true", help="Désactiver l'analyse algorithmique")
    parser.add_argument("--learn-pdf", help="Chemin vers un PDF pour enrichir la base de connaissances")
    parser.add_argument("--suggest", action="store_true", help="Activer les suggestions d'optimisation basées sur ACEOB")
    args = parser.parse_args()

    # Gestion de l'apprentissage PDF
    if args.learn_pdf:
        if not Path(args.learn_pdf).exists():
            print(f"Erreur : fichier PDF {args.learn_pdf} introuvable.", file=sys.stderr)
            sys.exit(1)
        new_patterns = add_patterns_from_pdf(args.learn_pdf)
        print(f"{len(new_patterns)} nouveau(x) motif(s) ajouté(s).")
        if not args.paths:
            return

    # Collecte des fichiers Python
    py_files = collect_py_files(args.paths, args.recursive)
    if not py_files:
        print("Aucun fichier Python trouvé.", file=sys.stderr)
        sys.exit(0)

    # Initialisation de l'indexeur ACEOB si demandé
    indexer = CodeOptimizationIndexer(sample_size=5000)
    if args.suggest:
        if INDEXER_AVAILABLE:
            try:
                indexer = CodeOptimizationIndexer(sample_size=5000)  # ajustez selon vos besoins
                print("Indexeur ACEOB initialisé.")
            except Exception as e:
                print(f"Erreur lors de l'initialisation de l'indexeur ACEOB : {e}", file=sys.stderr)
        else:
            print("Indexeur ACEOB non disponible (module ai.code_indexer manquant).", file=sys.stderr)

    # Analyse de chaque fichier
    results = []
    for filepath in py_files:
        issues = analyze_file(filepath, config, args.no_pylint, args.no_algorithm)

        # Suggestions ACEOB
        if indexer:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                suggestions = indexer.suggest_optimization(source_code, top_k=2)
                for s in suggestions:
                    issues.append({
                        'line': 0,
                        'type': 'optimization',
                        'message': "Optimisation possible (basée sur ACEOB)",
                        'suggestion': f"Voici un exemple de code optimisé (similarité {s['similarity']:.2f}) :\n{s['efficient']}",
                        'explanation': "Cette suggestion est basée sur des paires de code du dataset ACEOB."
                    })
            except Exception as e:
                print(f"Erreur lors de la suggestion pour {filepath}: {e}", file=sys.stderr)

        results.append({
            "file": str(filepath),
            "issues": issues
        })

    # Génération de la sortie
    if args.output == "console":
        output_console(results)
    else:
        output_json(results, args.output_file)

if __name__ == "__main__":
    main()