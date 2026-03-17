import ast
import tokenize
from pathlib import Path
from io import BytesIO
from typing import List, Dict, Any, Optional, Union

class CodeParser:
    """
    Analyse un fichier Python et fournit son AST et des métadonnées.
    
    Attributes:
        filepath (Path): Chemin du fichier analysé.
        source (str): Contenu du fichier.
        tree (ast.AST): Arbre syntaxique.
        lines (List[str]): Lignes du fichier.
    """
    
    def __init__(self, filepath: Union[str, Path]):
        """
        Initialise le parser avec un fichier Python.
        
        Args:
            filepath: Chemin vers le fichier Python.
        
        Raises:
            FileNotFoundError: Si le fichier n'existe pas.
            SyntaxError: Si le fichier contient des erreurs de syntaxe.
        """
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"Fichier introuvable : {filepath}")
        
        self.source = self.filepath.read_text(encoding='utf-8')
        try:
            self.tree = ast.parse(self.source)
        except SyntaxError as e:
            # On peut enrichir l'erreur avec le contexte
            raise SyntaxError(f"Erreur de syntaxe dans {filepath} : {e}")
        
        self.lines = self.source.splitlines()
    
    # ================== Méthodes de base ==================
    
    def get_lines(self, start: int = 1, end: Optional[int] = None) -> List[str]:
        """
        Retourne les lignes du fichier (numérotation à partir de 1).
        
        Args:
            start: Première ligne incluse (1-indexé).
            end: Dernière ligne incluse (inclus, None = jusqu'à la fin).
        
        Returns:
            Liste des lignes demandées.
        """
        if end is None:
            end = len(self.lines)
        return self.lines[start-1:end]
    
    def get_node_at_line(self, line: int) -> Optional[ast.AST]:
        """
        Retourne le premier nœud trouvé à une ligne donnée (utile pour le rapport).
        
        Args:
            line: Numéro de ligne (1-indexé).
        
        Returns:
            Nœud AST ou None si aucun trouvé.
        """
        for node in ast.walk(self.tree):
            if hasattr(node, 'lineno') and node.lineno == line:
                return node
        return None
    
    # ================== Extraction des nœuds ==================
    
    def get_functions(self) -> List[ast.FunctionDef]:
        """Retourne toutes les fonctions définies dans le fichier (y compris les méthodes)."""
        return [node for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef)]
    
    def get_classes(self) -> List[ast.ClassDef]:
        """Retourne toutes les classes définies."""
        return [node for node in ast.walk(self.tree) if isinstance(node, ast.ClassDef)]
    
    def get_imports(self) -> List[Union[ast.Import, ast.ImportFrom]]:
        """Retourne tous les imports."""
        return [node for node in ast.walk(self.tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    
    def get_assignments(self) -> List[ast.Assign]:
        """Retourne toutes les assignations (variables globales)."""
        return [node for node in ast.walk(self.tree) if isinstance(node, ast.Assign)]
    
    def get_functions_detailed(self) -> List[Dict[str, Any]]:
        """
        Retourne une liste détaillée des fonctions avec métadonnées.
        
        Returns:
            Liste de dictionnaires avec les clés : name, lineno, end_lineno, docstring, args.
        """
        functions = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'lineno': node.lineno,
                    'end_lineno': getattr(node, 'end_lineno', node.lineno),  # Python 3.8+
                    'docstring': ast.get_docstring(node),
                    'args': [arg.arg for arg in node.args.args],
                })
        return functions
    
    # ================== Extraction des noms ==================
    
    def get_all_names(self) -> List[Dict[str, Any]]:
        """
        Retourne tous les identifiants (variables, fonctions, classes, attributs, paramètres)
        avec leur type et leur ligne.
        
        Returns:
            Liste de dictionnaires : {'id': str, 'lineno': int, 'type': str, ...}
        """
        names = []
        
        for node in ast.walk(self.tree):
            # Noms simples (variables, attributs)
            if isinstance(node, ast.Name):
                names.append({
                    'id': node.id,
                    'lineno': node.lineno,
                    'type': 'name',
                    'ctx': type(node.ctx).__name__
                })
            # Attributs (objet.attr)
            elif isinstance(node, ast.Attribute):
                names.append({
                    'id': node.attr,
                    'lineno': node.lineno,
                    'type': 'attribute',
                    'ctx': type(node.ctx).__name__
                })
            # Définitions de fonctions
            elif isinstance(node, ast.FunctionDef):
                names.append({
                    'id': node.name,
                    'lineno': node.lineno,
                    'type': 'function'
                })
                # Ajouter les paramètres
                for arg in node.args.args:
                    names.append({
                        'id': arg.arg,
                        'lineno': node.lineno,  # approximatif (les paramètres n'ont pas de ligne propre)
                        'type': 'parameter'
                    })
            # Définitions de classes
            elif isinstance(node, ast.ClassDef):
                names.append({
                    'id': node.name,
                    'lineno': node.lineno,
                    'type': 'class'
                })
            # Noms dans les compréhensions (ex: for x in ...)
            elif isinstance(node, ast.comprehension):
                if isinstance(node.target, ast.Name):
                    names.append({
                        'id': node.target.id,
                        'lineno': node.target.lineno,
                        'type': 'comprehension_var'
                    })
            # Noms dans les alias d'import (import ... as ...)
            elif isinstance(node, ast.alias):
                names.append({
                    'id': node.asname if node.asname else node.name,
                    'lineno': 0,  # l'import n'a pas de ligne dans l'alias
                    'type': 'import_alias'
                })
        
        return names
    
    # ================== Extraction des chaînes ==================
    
    def get_string_tokens(self) -> List[tokenize.TokenInfo]:
        """
        Retourne tous les tokens de type STRING du fichier.
        Utilise tokenize pour préserver les délimiteurs exacts.
        
        Returns:
            Liste des tokens de chaîne.
        """
        tokens = []
        source_bytes = self.source.encode('utf-8')
        try:
            for tok in tokenize.tokenize(BytesIO(source_bytes).readline):
                if tok.type == tokenize.STRING:
                    tokens.append(tok)
        except tokenize.TokenError as e:
            # Gérer les chaînes mal formées (ex: fichier tronqué)
            # On ignore simplement et on retourne ce qu'on a pu récupérer
            pass
        return tokens
    
    def extract_comments(self) -> List[Dict[str, Any]]:
        """
        Extrait les commentaires du fichier en utilisant tokenize.
        
        Returns:
            Liste de dictionnaires : {'line': int, 'text': str}
        """
        comments = []
        source_bytes = self.source.encode('utf-8')
        try:
            for tok in tokenize.tokenize(BytesIO(source_bytes).readline):
                if tok.type == tokenize.COMMENT:
                    comments.append({
                        'line': tok.start[0],
                        'text': tok.string
                    })
        except tokenize.TokenError:
            pass
        return comments