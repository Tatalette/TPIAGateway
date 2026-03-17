# knowledge/matcher.py
import ast
from typing import List
from knowledge.knowledge_base import PATTERNS, AlgorithmPattern

class AlgorithmMatcher:
    def __init__(self):
        self.patterns = PATTERNS

    def match_function(self, func_node: ast.FunctionDef) -> List[AlgorithmPattern]:
        """Teste tous les motifs sur une fonction et retourne ceux qui correspondent."""
        matches = []
        for pattern in self.patterns:
            if pattern.detector(func_node):
                matches.append(pattern)
        return matches