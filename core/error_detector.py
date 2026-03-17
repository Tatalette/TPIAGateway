import subprocess
import json
from typing import List, Dict, Any, Optional
from core.parser import CodeParser

class PylintErrorDetector:
    """Utilise pylint pour détecter des erreurs et problèmes dans le code."""

    def __init__(self, parser: CodeParser, pylint_path: str = "pylint"):
        self.parser = parser
        self.pylint_path = pylint_path
        self.issues = []

    def check(self) -> List[Dict[str, Any]]:
        """Exécute pylint et retourne la liste des problèmes détectés."""
        try:
            result = subprocess.run(
                [self.pylint_path, str(self.parser.filepath), "-f", "json"],
                capture_output=True,
                text=True,
                check=False  # pylint peut retourner un code non nul même en cas de succès (s'il trouve des problèmes)
            )
            if result.returncode not in (0, 2, 4, 8, 16, 32):
                # Gestion des erreurs graves de pylint (fichier inexistant, etc.)
                self.issues.append({
                    'line': 0,
                    'type': 'pylint_error',
                    'message': f"Erreur lors de l'exécution de pylint : {result.stderr}",
                })
                return self.issues

            # Parser la sortie JSON
            if result.stdout.strip():
                data = json.loads(result.stdout)
                for item in data:
                    issue = self._convert_pylint_item(item)
                    if issue:
                        self.issues.append(issue)
        except FileNotFoundError:
            self.issues.append({
                'line': 0,
                'type': 'pylint_not_found',
                'message': "pylint n'est pas installé. Veuillez l'installer avec 'pip install pylint' pour activer cette analyse.",
            })
        except Exception as e:
            self.issues.append({
                'line': 0,
                'type': 'pylint_exception',
                'message': f"Exception inattendue lors de l'appel à pylint : {str(e)}",
            })
        return self.issues

    def _convert_pylint_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convertit un élément pylint en issue interne."""
        # On peut filtrer certains types si on veut (par exemple ignorer les conventions si on les gère déjà)
        # Pour l'instant on garde tout
        return {
            'line': item.get('line', 0),
            'column': item.get('column', 0),
            'type': 'pylint',
            'pylint_type': item.get('type'),
            'symbol': item.get('symbol'),
            'message': item.get('message'),
            'suggestion': self._get_suggestion(item.get('symbol')),
        }

    def _get_suggestion(self, symbol: str) -> Optional[str]:
        """Fournit une suggestion personnalisée pour certains symboles connus."""
        suggestions = {
            'unused-variable': "Supprimez cette variable ou utilisez-la.",
            'unused-import': "Supprimez cet import inutilisé.",
            'missing-docstring': "Ajoutez une docstring pour documenter ce que fait cette fonction/classe.",
            'trailing-whitespace': "Supprimez les espaces en fin de ligne.",
        }
        return suggestions.get(symbol)