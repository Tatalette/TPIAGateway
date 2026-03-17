# core/issue.py
from typing import Optional, Dict, Any

class Issue:
    """Représente un problème détecté par l'un des modules d'analyse."""

    def __init__(self, line: int, issue_type: str, message: str, suggestion: Optional[str] = None, **kwargs):
        """
        Initialise une issue.

        :param line: Numéro de ligne (0 pour un problème global).
        :param issue_type: Type d'issue (ex: 'naming', 'quotes', 'pylint', 'algorithm').
        :param message: Description du problème.
        :param suggestion: Suggestion de correction (optionnelle).
        :param kwargs: Attributs supplémentaires (ex: 'subtype', 'symbol', etc.).
        """
        self.line = line
        self.type = issue_type
        self.message = message
        self.suggestion = suggestion
        self.extra = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'issue en dictionnaire pour faciliter la génération de rapports."""
        d = {
            'line': self.line,
            'type': self.type,
            'message': self.message,
        }
        if self.suggestion:
            d['suggestion'] = self.suggestion
        d.update(self.extra)
        return d