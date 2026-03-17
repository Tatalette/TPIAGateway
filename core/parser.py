import ast
import tokenize
from pathlib import Path
from typing import List, Dict, Any, Optional

class CodeParser:
    """Analyse un fichier Python et fournit son AST et des métadonnées."""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"Fichier introuvable : {filepath}")
        self.source = self.filepath.read_text(encoding='utf-8')
        self.tree = ast.parse(self.source)
        self.lines = self.source.splitlines()
        
    def get_functions(self) -> List[ast.FunctionDef]:
        """Retourne toutes les fonctions définies dans le fichier."""
        return [node for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef)]
    
    def get_classes(self) -> List[ast.ClassDef]:
        """Retourne toutes les classes définies."""
        return [node for node in ast.walk(self.tree) if isinstance(node, ast.ClassDef)]
    
    def get_variable_assignments(self) -> List[ast.Assign]:
        """Retourne toutes les assignations (variables globales)."""
        return [node for node in ast.walk(self.tree) if isinstance(node, ast.Assign)]
    
    def get_imports(self) -> List[ast.Import | ast.ImportFrom]:
        """Retourne tous les imports."""
        imports = []
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
        return imports
    
    def get_node_at_line(self, line: int) -> Optional[ast.AST]:
        """Retourne le premier nœud trouvé à une ligne donnée (utile pour le rapport)."""
        for node in ast.walk(self.tree):
            if hasattr(node, 'lineno') and node.lineno == line:
                return node
        return None
    
    def extract_comments(self) -> List[Dict[str, Any]]:
        """Extrait les commentaires du fichier en utilisant tokenize."""
        comments = []
        with open(self.filepath, 'rb') as f:
            for tok in tokenize.tokenize(f.readline):
                if tok.type == tokenize.COMMENT:
                    comments.append({
                        'line': tok.start[0],
                        'text': tok.string
                    })
        return comments
    
    # Exemple de méthode utilitaire pour vérifier les noms (sera utilisée par style_checker)
    def get_all_names(self) -> List[Dict[str, Any]]:
        """Retourne tous les noms (variables, fonctions, classes) avec leur type et ligne."""
        names = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name):
                names.append({
                    'id': node.id,
                    'lineno': node.lineno,
                    'ctx': type(node.ctx).__name__  # Load, Store, Del
                })
            elif isinstance(node, ast.FunctionDef):
                names.append({
                    'id': node.name,
                    'lineno': node.lineno,
                    'type': 'function'
                })
            elif isinstance(node, ast.ClassDef):
                names.append({
                    'id': node.name,
                    'lineno': node.lineno,
                    'type': 'class'
                })
        return names
