# knowledge/knowledge_base.py
import ast
from typing import Callable, List, Dict, Any

class AlgorithmPattern:
    def __init__(self, name: str, description: str, detector: Callable, suggestion: str, explanation: str, source: str = ""):
        self.name = name
        self.description = description
        self.detector = detector
        self.suggestion = suggestion
        self.explanation = explanation
        self.source = source

# Fonctions de détection

def detect_bubble_sort(func_node: ast.FunctionDef) -> bool:
    """Détecte un tri à bulles : deux boucles for imbriquées avec échange conditionnel."""
    has_nested_loops = False
    has_swap = False

    for node in ast.walk(func_node):
        if isinstance(node, ast.For):
            # Cherche une deuxième boucle for dans le corps
            for inner in ast.walk(node):
                if inner is not node and isinstance(inner, ast.For):
                    has_nested_loops = True
                # Cherche un échange de type a, b = b, a
                if isinstance(inner, ast.Assign) and isinstance(inner.value, ast.Tuple):
                    if len(inner.value.elts) == 2 and len(inner.targets) == 1 and isinstance(inner.targets[0], ast.Tuple):
                        # C'est probablement un swap
                        has_swap = True
    return has_nested_loops and has_swap

def detect_linear_search(func_node: ast.FunctionDef) -> bool:
    """Détecte une recherche linéaire : boucle for/while avec comparaison et return dans la boucle."""
    has_loop = False
    has_comparison = False
    has_return_in_loop = False

    for node in ast.walk(func_node):
        if isinstance(node, (ast.For, ast.While)):
            has_loop = True
            # Parcourir le corps de la boucle
            for inner in ast.walk(node):
                if isinstance(inner, ast.If):
                    # Vérifie si le if contient une comparaison (peut être simplifié)
                    has_comparison = True
                if isinstance(inner, ast.Return):
                    has_return_in_loop = True
    return has_loop and has_comparison and has_return_in_loop

def detect_binary_search(func_node: ast.FunctionDef) -> bool:
    """Détecte une recherche dichotomique : boucle while avec indices low/high et comparaison."""
    has_while = False
    has_low_high = False
    has_mid = False

    for node in ast.walk(func_node):
        if isinstance(node, ast.While):
            has_while = True
        # Cherche des noms comme 'low', 'high', 'mid' (approximatif)
        if isinstance(node, ast.Name) and node.id in ('low', 'high', 'mid', 'gauche', 'droite', 'milieu'):
            has_low_high = True
        # Cherche une affectation de type mid = (low + high) // 2
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.FloorDiv):
                if isinstance(node.value.left, ast.BinOp) and isinstance(node.value.left.op, ast.Add):
                    # Peut-être (low + high) // 2
                    has_mid = True
    return has_while and has_low_high and has_mid

def detect_quick_sort(func_node: ast.FunctionDef) -> bool:
    """Détecte un tri rapide récursif simple : fonction récursive avec partitionnement."""
    # Vérifie si la fonction s'appelle elle-même
    has_recursion = False
    has_partition = False

    for node in ast.walk(func_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == func_node.name:
            has_recursion = True
        # Cherche une compréhension de liste pour partition (gauche/droite)
        if isinstance(node, ast.ListComp):
            # Exemple: [x for x in arr[1:] if x <= pivot]
            has_partition = True
        if isinstance(node, ast.For) and isinstance(node.iter, ast.ListComp):
            has_partition = True
    return has_recursion and has_partition

# Base de connaissances enrichie
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
    ),
    AlgorithmPattern(
        name="recherche_dichotomique",
        description="Recherche dichotomique (recherche binaire) probable",
        detector=detect_binary_search,
        suggestion="Votre implémentation de recherche binaire semble correcte. Cependant, vous pouvez utiliser le module `bisect` qui offre des fonctions optimisées : `bisect_left`, `bisect_right`, etc.",
        explanation="La recherche dichotomique est efficace (O(log n)), mais l'utilisation du module `bisect` (implémenté en C) est encore plus rapide pour les listes triées.",
        source="Source interne"
    ),
    AlgorithmPattern(
        name="tri_rapide_maison",
        description="Tri rapide (implémentation récursive personnelle)",
        detector=detect_quick_sort,
        suggestion="Pour trier, préférez `sorted()` ou `list.sort()` qui sont plus rapides et évitent les problèmes de récursion profonde.",
        explanation="Les tris récursifs maison en Python peuvent être lents et risquent de dépasser la limite de récursion pour de grandes listes. Les fonctions natives sont optimisées en C.",
        source="Source interne"
    ),
]