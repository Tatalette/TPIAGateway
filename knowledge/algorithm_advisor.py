# knowledge/algorithm_advisor.py
import ast
from typing import List
from core.parser import CodeParser
from core.issue import Issue
from knowledge.matcher import AlgorithmMatcher

class AlgorithmAdvisor:
    def __init__(self, parser: CodeParser):
        self.parser = parser
        self.matcher = AlgorithmMatcher()
        self.issues: List[Issue] = []

    def analyze(self) -> List[Issue]:
        functions = self.parser.get_functions()
        for func in functions:
            # Obtenir le code source de la fonction
            func_source = ast.get_source_segment(self.parser.source, func)
            if not func_source:
                continue
            matches = self.matcher.match_function(func, func_source)
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