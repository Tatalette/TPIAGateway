import re
import ast
from typing import List, Dict, Any
from core.parser import CodeParser

class StyleChecker:
    """Vérifie les conventions de style dans un fichier Python."""

    # Patterns de validation
    SNAKE_CASE = re.compile(r'^[a-z_][a-z0-9_]*$')
    CAMEL_CASE = re.compile(r'^[A-Z][a-zA-Z0-9]*$')

    def __init__(self, parser: CodeParser):
        self.parser = parser
        self.issues = []

    def check_all(self) -> List[Dict[str, Any]]:
        """Exécute toutes les vérifications de style."""
        self.check_naming_conventions()
        self.check_quotes_consistency()
        return self.issues

    def check_naming_conventions(self):
        """Vérifie que les noms respectent les conventions Python."""
        names = self.parser.get_all_names()
        for name_info in names:
            name = name_info['id']
            lineno = name_info['lineno']
            name_type = name_info.get('type', 'variable')  # par défaut variable

            if name_type == 'class':
                if not self.CAMEL_CASE.match(name):
                    self.issues.append({
                        'line': lineno,
                        'type': 'naming',
                        'subtype': 'class_case',
                        'message': f"Le nom de classe '{name}' devrait être en CamelCase (ex: MaClasse).",
                        'suggestion': self._suggest_camel_case(name)
                    })
            else:  # fonction ou variable
                if not self.SNAKE_CASE.match(name):
                    self.issues.append({
                        'line': lineno,
                        'type': 'naming',
                        'subtype': 'snake_case',
                        'message': f"Le nom '{name}' devrait être en snake_case (ex: ma_variable).",
                        'suggestion': self._suggest_snake_case(name)
                    })

    def check_quotes_consistency(self):
        """Vérifie que les guillemets sont cohérents dans tout le fichier."""
        tokens = self._get_string_tokens()
        single_quotes = 0
        double_quotes = 0
        for token in tokens:
            if token.string.startswith("'") and not token.string.startswith("'''"):
                single_quotes += 1
            elif token.string.startswith('"') and not token.string.startswith('"""'):
                double_quotes += 1

        if single_quotes > 0 and double_quotes > 0:
            preferred = "'" if single_quotes >= double_quotes else '"'
            self.issues.append({
                'line': 0,
                'type': 'quotes',
                'message': "Mélange de guillemets simples et doubles dans les chaînes.",
                'suggestion': f"Utilisez uniformément des guillemets {preferred} (préférence pour le plus fréquent)."
            })

    def _get_string_tokens(self):
        """Extrait les tokens de type STRING en utilisant tokenize."""
        import tokenize
        from io import BytesIO
        tokens = []
        source_bytes = self.parser.source.encode('utf-8')
        for tok in tokenize.tokenize(BytesIO(source_bytes).readline):
            if tok.type == tokenize.STRING:
                tokens.append(tok)
        return tokens

    @staticmethod
    def _suggest_snake_case(name: str) -> str:
        """Convertit un nom en snake_case (simple heuristique)."""
        # Exemple: 'maVariable' -> 'ma_variable'
        s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
        return s.lower()

    @staticmethod
    def _suggest_camel_case(name: str) -> str:
        """Convertit un nom en CamelCase."""
        # snake_case to CamelCase
        return ''.join(word.capitalize() for word in name.split('_'))