import subprocess
import json
from typing import List, Dict, Any, Optional
from core.parser import CodeParser
from core.issue import Issue

class PylintErrorDetector:
    """Utilise pylint pour détecter des erreurs et problèmes dans le code."""

    def __init__(self, parser: CodeParser, pylint_path: str = "pylint"):
        self.parser = parser
        self.pylint_path = pylint_path
        self.issues: List[Issue] = []

    def check(self) -> List[Issue]:
        """Exécute pylint et retourne la liste des problèmes détectés."""
        try:
            result = subprocess.run(
                [self.pylint_path, str(self.parser.filepath), "-f", "json"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    if isinstance(data, list):
                        for item in data:
                            self.issues.append(self._convert_pylint_item(item))
                    else:
                        self.issues.append(Issue(
                            line=0,
                            issue_type='pylint_error',
                            message=f"Format JSON inattendu : {result.stdout[:200]}"
                        ))
                except json.JSONDecodeError as e:
                    self.issues.append(Issue(
                        line=0,
                        issue_type='pylint_error',
                        message=f"Erreur de décodage JSON : {e}. Sortie : {result.stdout[:200]}"
                    ))
            else:
                if result.stderr:
                    self.issues.append(Issue(
                        line=0,
                        issue_type='pylint_error',
                        message=f"Erreur pylint : {result.stderr}"
                    ))

        except FileNotFoundError:
            self.issues.append(Issue(
                line=0,
                issue_type='pylint_not_found',
                message="pylint n'est pas installé. Veuillez l'installer avec 'pip install pylint' pour activer cette analyse."
            ))
        except Exception as e:
            self.issues.append(Issue(
                line=0,
                issue_type='pylint_exception',
                message=f"Exception inattendue : {str(e)}"
            ))

        return self.issues

    def _convert_pylint_item(self, item: Dict[str, Any]) -> Issue:
        """Convertit un élément pylint en issue interne."""
        return Issue(
            line=item.get('line', 0),
            issue_type='pylint',
            message=item.get('message', ''),
            suggestion=self._get_suggestion(item.get('symbol')),
            pylint_type=item.get('type'),
            symbol=item.get('symbol'),
        )

    def _get_suggestion(self, symbol: str) -> Optional[str]:
        """Fournit une suggestion personnalisée pour certains symboles connus."""
        suggestions = {
            'unused-variable': "Supprimez cette variable ou utilisez-la.",
            'unused-import': "Supprimez cet import inutilisé.",
            'missing-docstring': "Ajoutez une docstring pour documenter ce que fait cette fonction/classe.",
            'trailing-whitespace': "Supprimez les espaces en fin de ligne.",
        }
        return suggestions.get(symbol)