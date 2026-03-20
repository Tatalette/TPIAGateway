# knowledge/matcher.py
import ast
from typing import List
from knowledge.knowledge_base import PATTERNS, AlgorithmPattern

class AlgorithmMatcher:
    def match_function(self, func_node: ast.FunctionDef, source: str) -> List[AlgorithmPattern]:
        matches = []
        for pattern in self.patterns:
            if pattern.detector(func_node, source):
                matches.append(pattern)
        return matches