# knowledge/knowledge_base.py
import ast
from typing import Callable, Dict, Any

class AlgorithmPattern:
    def __init__(self, name: str, description: str, detector: Callable, suggestion: str, explanation: str, source: str = ""):
        self.name = name
        self.description = description
        self.detector = detector
        self.suggestion = suggestion
        self.explanation = explanation
        self.source = source

# Fonctions de détection spécifiques
def detect_bubble_sort(func_node: ast.FunctionDef) -> bool:
    """Détecte un tri à bulles naïf : deux boucles for imbriquées avec échange d'éléments."""
    has_nested_loops = False
    has_swap = False
    for node in ast.walk(func_node):
        # Cherche deux boucles for imbriquées
        if isinstance(node, ast.For):
            # Regarde si dans le corps de cette boucle il y a une autre boucle for
            for inner in ast.walk(node):
                if inner is not node and isinstance(inner, ast.For):
                    has_nested_loops = True
                # Cherche un échange du type a, b = b, a (ast.Tuple dans une assignation)
                if isinstance(inner, ast.Assign) and isinstance(inner.value, ast.Tuple):
                    # Si on échange deux variables, c'est probablement un swap
                    if len(inner.value.elts) == 2 and len(inner.targets) == 1 and isinstance(inner.targets[0], ast.Tuple):
                        has_swap = True
    return has_nested_loops and has_swap

def detect_linear_search(func_node: ast.FunctionDef) -> bool:
    """Détecte une recherche linéaire simple : boucle for avec comparaison et return."""
    has_loop = False
    has_comparison = False
    has_return_in_loop = False
    for node in ast.walk(func_node):
        if isinstance(node, ast.For) or isinstance(node, ast.While):
            has_loop = True
            # Cherche une comparaison (if) dans la boucle
            for inner in ast.walk(node):
                if isinstance(inner, ast.If):
                    has_comparison = True
                if isinstance(inner, ast.Return):
                    has_return_in_loop = True
    return has_loop and has_comparison and has_return_in_loop

# Base de connaissances initiale
PATTERNS = [
    AlgorithmPattern(
        name="tri_bulle",
        description="Tri à bulles (implémentation naïve)",
        detector=detect_bubble_sort,
        suggestion="Utilisez la fonction native `sorted()` ou la méthode `list.sort()` qui sont implémentées en C et beaucoup plus rapides (Timsort, complexité O(n log n)).",
        explanation="Le tri à bulles a une complexité moyenne de O(n²), ce qui le rend inefficace sur de grandes listes. Les algorithmes intégrés en Python sont optimisés et bien plus performants.",
        source="Source interne"
    ),
    AlgorithmPattern(
        name="recherche_lineaire",
        description="Recherche linéaire dans une liste",
        detector=detect_linear_search,
        suggestion="Si la liste est triée, utilisez la recherche dichotomique (`bisect` module) pour une complexité O(log n) au lieu de O(n). Sinon, envisagez d'utiliser un ensemble (`set`) si vous faites plusieurs recherches.",
        explanation="La recherche linéaire parcourt toute la liste, ce qui est inefficace pour de grandes données. Des structures comme les ensembles ou la recherche binaire peuvent considérablement améliorer les performances.",
        source="Source interne"
    )
]