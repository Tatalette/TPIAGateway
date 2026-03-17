# knowledge/algorithm_advisor.py
import ast
from typing import List, Dict, Any
from core.parser import CodeParser
from core.issue import Issue
from knowledge.knowledge_base import PATTERNS, AlgorithmPattern
from knowledge.matcher import AlgorithmMatcher

class AlgorithmAdvisor:
    """Analyse le code à la recherche d'opportunités d'optimisation algorithmique."""

    def __init__(self, parser: CodeParser):
        self.parser = parser
        self.matcher = AlgorithmMatcher()
        self.issues: List[Issue] = []

    def analyze(self) -> List[Issue]:
        """Parcourt toutes les fonctions et détecte les motifs algorithmiques."""
        functions = self.parser.get_functions()
        for func in functions:
            matches = self.matcher.match_function(func)
            for pattern in matches:
                self.issues.append(Issue(
                    line=func.lineno,
                    issue_type='algorithm',
                    message=f"Fonction '{func.name}' : {pattern.description} détecté.",
                    suggestion=pattern.suggestion,
                    explanation=pattern.explanation,
                    pattern=pattern.name,
                    source=pattern.source
                ))
        return self.issues