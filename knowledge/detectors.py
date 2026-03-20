# knowledge/detectors.py
import ast
from typing import List, Callable

def make_keyword_detector(keywords: List[str]) -> Callable[[ast.FunctionDef], bool]:
    """
    Retourne un détecteur qui vérifie si le code source de la fonction contient
    l'un des mots-clés (recherche insensible à la casse).
    """
    def make_keyword_detector(keywords: List[str]) -> Callable:
        def keyword_detector(func_node: ast.FunctionDef, source: str) -> bool:
            source_lower = source.lower()
            for kw in keywords:
                if kw.lower() in source_lower:
                    return True
            return False
        return keyword_detector