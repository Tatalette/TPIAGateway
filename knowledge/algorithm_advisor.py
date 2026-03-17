# knowledge/algorithm_advisor.py
from typing import List, Dict, Any
from core.parser import CodeParser
from knowledge.matcher import AlgorithmMatcher

class AlgorithmAdvisor:
    """Analyse le code à la recherche d'opportunités d'optimisation algorithmique."""

    def __init__(self, parser: CodeParser):
        self.parser = parser
        self.matcher = AlgorithmMatcher()
        self.issues = []

    def analyze(self) -> List[Dict[str, Any]]:
        """Parcourt toutes les fonctions et détecte les motifs algorithmiques."""
        functions = self.parser.get_functions()
        for func in functions:
            matches = self.matcher.match_function(func)
            for pattern in matches:
                self.issues.append({
                    'line': func.lineno,
                    'type': 'algorithm',
                    'pattern': pattern.name,
                    'message': f"Fonction '{func.name}' : {pattern.description} détecté.",
                    'suggestion': pattern.suggestion,
                    'explanation': pattern.explanation,
                    'source': pattern.source
                })
        return self.issues