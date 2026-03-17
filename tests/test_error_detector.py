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

    # On doit trouver au moins unused-import et unused-variable
    symbols = [i['symbol'] for i in issues if i.get('symbol')]
    assert 'unused-import' in symbols
    assert 'unused-variable' in symbols

def test_pylint_not_installed_graceful_failure(monkeypatch):
    # Simuler l'absence de pylint en faisant échouer subprocess.run
    def mock_run(*args, **kwargs):
        raise FileNotFoundError("pylint not found")
    monkeypatch.setattr(subprocess, 'run', mock_run)

    parser = CodeParser("dummy.py")  # fichier inexistant mais pas utilisé
    detector = PylintErrorDetector(parser)
    issues = detector.check()
    assert len(issues) == 1
    assert issues[0]['type'] == 'pylint_not_found'