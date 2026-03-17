import pytest
import subprocess
from core.parser import CodeParser
from core.error_detector import PylintErrorDetector

@pytest.fixture
def sample_file_with_pylint_issues(tmp_path):
    content = """
import os  # unused import

def fonction():
    x = 1  # unused variable
    return 0
"""
    filepath = tmp_path / "sample_pylint.py"
    filepath.write_text(content)
    return filepath

def test_pylint_detector_finds_issues(sample_file_with_pylint_issues):
    parser = CodeParser(str(sample_file_with_pylint_issues))
    detector = PylintErrorDetector(parser)
    issues = detector.check()

    # Vérifier qu'on a bien des issues
    assert len(issues) > 0, "Aucune issue retournée par pylint"

    # Extraire les symboles
    symbols = []
    for issue in issues:
        if issue.extra.get('symbol'):
            symbols.append(issue.extra['symbol'])

    # Afficher pour débogage en cas d'échec
    if 'unused-import' not in symbols:
        print("\nIssues reçues :")
        for issue in issues:
            print(f"  {issue.line}: {issue.message} (symbol: {issue.extra.get('symbol')})")
        print(f"Symbols extraits : {symbols}")

    assert 'unused-import' in symbols
    assert 'unused-variable' in symbols

def test_pylint_not_installed_graceful_failure(monkeypatch, tmp_path):
    # Créer un fichier valide pour éviter l'erreur de CodeParser
    dummy_file = tmp_path / "dummy.py"
    dummy_file.touch()

    def mock_run(*args, **kwargs):
        raise FileNotFoundError("pylint not found")
    monkeypatch.setattr(subprocess, 'run', mock_run)

    parser = CodeParser(str(dummy_file))
    detector = PylintErrorDetector(parser)
    issues = detector.check()
    assert len(issues) == 1
    assert issues[0].type == 'pylint_not_found'