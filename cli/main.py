import argparse
from pathlib import Path
from core.parser import CodeParser
from core.style_checker import StyleChecker
from core.error_detector import PylintErrorDetector
from knowledge.algorithm_advisor import AlgorithmAdvisor

def main():
    parser = argparse.ArgumentParser(description="Revue de code Python")
    parser.add_argument("file", help="Fichier Python à analyser")
    parser.add_argument("--no-pylint", action="store_true", help="Désactiver l'analyse pylint")
    parser.add_argument("--no-algorithm", action="store_true", help="Désactiver l'analyse algorithmique")
    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"Erreur : fichier {args.file} introuvable.")
        return

    code_parser = CodeParser(args.file)
    all_issues = []

    # Style checker (retourne des objets Issue)
    style_checker = StyleChecker(code_parser)
    style_issues = style_checker.check_all()
    all_issues.extend([issue.to_dict() for issue in style_issues])

    # Pylint error detector (retourne des objets Issue maintenant)
    if not args.no_pylint:
        pylint_detector = PylintErrorDetector(code_parser)
        pylint_issues = pylint_detector.check()
        all_issues.extend([issue.to_dict() for issue in pylint_issues])  # conversion en dict

    # Algorithm advisor
    if not args.no_algorithm:
        algorithm_advisor = AlgorithmAdvisor(code_parser)
        algorithm_issues = algorithm_advisor.analyze()
        all_issues.extend([issue.to_dict() for issue in algorithm_issues])

    if all_issues:
        print(f"{len(all_issues)} problème(s) détecté(s) :\n")
        for issue in all_issues:
            line_info = f"ligne {issue['line']}" if issue.get('line') else "fichier"
            print(f"- {line_info} : {issue['message']}")
            if 'suggestion' in issue and issue['suggestion']:
                print(f"  Suggestion : {issue['suggestion']}")
            if 'explanation' in issue:
                print(f"  Explication : {issue['explanation']}")
    else:
        print("Aucun problème détecté.")

if __name__ == "__main__":
    main()