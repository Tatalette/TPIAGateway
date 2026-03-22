# knowledge/detectors.py
import ast
from typing import List, Callable

def make_keyword_detector(keywords: List[str]) -> Callable:
    """Crée un détecteur qui recherche les mots-clés dans le source de la fonction."""
    def keyword_detector(func_node: ast.FunctionDef, source: str) -> bool:
        source_lower = source.lower()
        for kw in keywords:
            if kw.lower() in source_lower:
                return True
        return False
    return keyword_detector