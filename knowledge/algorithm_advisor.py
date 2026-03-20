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

    def analyze(self):
    functions = self.parser.get_functions()
    for func in functions:
        # Extraire le texte de la fonction depuis self.parser.source
        # On peut utiliser ast.get_source_segment(self.parser.source, func)
        # Pour Python >= 3.8
        func_source = ast.get_source_segment(self.parser.source, func)
        if not func_source:
            continue
        matches = self.matcher.match_function(func, func_source)
        for pattern in matches:
            self.issues.append(...)