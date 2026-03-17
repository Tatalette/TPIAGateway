# core/style_checker.py
import re
import tokenize
from io import BytesIO
from typing import List
from core.parser import CodeParser
from core.issue import Issue

class StyleChecker:
    """Vérifie les conventions de style dans un fichier Python."""

    SNAKE_CASE = re.compile(r'^[a-z_][a-z0-9_]*$')
    CAMEL_CASE = re.compile(r'^[A-Z][a-zA-Z0-9]*$')

    def __init__(self, parser: CodeParser):
        self.parser = parser
        self.issues: List[Issue] = []

    def check_all(self) -> List[Issue]:
        """Exécute toutes les vérifications de style."""
        self.check_naming_conventions()
        self.check_quotes_consistency()
        self.check_trailing_whitespace()
        return self.issues

    def check_naming_conventions(self):
        """Vérifie que les noms respectent les conventions Python."""
        names = self.parser.get_all_names()
        for name_info in names:
            name = name_info['id']
            lineno = name_info['lineno']
            name_type = name_info.get('type', 'variable')

            if name_type == 'class':
                if not self.CAMEL_CASE.match(name):
                    self.issues.append(Issue(
                        line=lineno,
                        issue_type='naming',
                        message=f"Le nom de classe '{name}' devrait être en CamelCase (ex: MaClasse).",
                        suggestion=self._suggest_camel_case(name),
                        subtype='class_case'
                    ))
            else:  # fonction ou variable
                if not self.SNAKE_CASE.match(name):
                    self.issues.append(Issue(
                        line=lineno,
                        issue_type='naming',
                        message=f"Le nom '{name}' devrait être en snake_case (ex: ma_variable).",
                        suggestion=self._suggest_snake_case(name),
                        subtype='snake_case'
                    ))

    def check_quotes_consistency(self):
        """Vérifie que les guillemets sont cohérents dans tout le fichier."""
        tokens = self._get_string_tokens()
        single_quotes = 0
        double_quotes = 0
        for token in tokens:
            s = token.string
            # Ignorer les triples quotes
            if s.startswith("'''") or s.startswith('"""'):
                continue
            # Chercher le premier guillemet (après préfixes éventuels)
            quote_char = None
            for ch in s:
                if ch in ('"', "'"):
                    quote_char = ch
                    break
            if quote_char == "'":
                single_quotes += 1
            elif quote_char == '"':
                double_quotes += 1

        if single_quotes > 0 and double_quotes > 0:
            preferred = "'" if single_quotes >= double_quotes else '"'
            self.issues.append(Issue(
                line=0,
                issue_type='quotes',
                message="Mélange de guillemets simples et doubles dans les chaînes.",
                suggestion=f"Utilisez uniformément des guillemets {preferred} (préférence pour le plus fréquent)."
            ))

    def check_trailing_whitespace(self):
        """Détecte les espaces en fin de ligne."""
        for i, line in enumerate(self.parser.lines, start=1):
            if line.rstrip() != line:
                self.issues.append(Issue(
                    line=i,
                    issue_type='trailing_whitespace',
                    message="Espace(s) en fin de ligne.",
                    suggestion="Supprimez les espaces inutiles en fin de ligne."
                ))

    def _get_string_tokens(self):
        """Extrait les tokens de type STRING en utilisant tokenize."""
        source_bytes = self.parser.source.encode('utf-8')
        tokens = []
        for tok in tokenize.tokenize(BytesIO(source_bytes).readline):
            if tok.type == tokenize.STRING:
                tokens.append(tok)
        return tokens

    @staticmethod
    def _suggest_snake_case(name: str) -> str:
        """Convertit un nom en snake_case (simple heuristique)."""
        s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
        return s.lower()

    @staticmethod
    def _suggest_camel_case(name: str) -> str:
        """Convertit un nom en CamelCase."""
        return ''.join(word.capitalize() for word in name.split('_'))