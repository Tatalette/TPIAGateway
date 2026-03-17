import pytest
from core.parser import CodeParser
from core.style_checker import StyleChecker
import ast

@pytest.fixture
def sample_file_with_issues(tmp_path):
    content = """
class maClasse:  # devrait être CamelCase
    def __init__(self):
        self.attributVariable = 1  # devrait être snake_case

def MaFonction():  # devrait être snake_case
    x = "hello" + 'world'  # mélange de guillemets
    return x
"""
    filepath = tmp_path / "sample_style.py"
    filepath.write_text(content)
    return filepath

def test_naming_issues(sample_file_with_issues):
    parser = CodeParser(str(sample_file_with_issues))
    checker = StyleChecker(parser)
    issues = checker.check_all()
    naming_issues = [i for i in issues if i['type'] == 'naming']
    assert len(naming_issues) == 3  # maClasse, attributVariable, MaFonction
    # Vérifions le détail
    lines = [i['line'] for i in naming_issues]
    assert 2 in lines  # maClasse
    assert 4 in lines  # attributVariable
    assert 6 in lines  # MaFonction

def test_quotes_issues(sample_file_with_issues):
    parser = CodeParser(str(sample_file_with_issues))
    checker = StyleChecker(parser)
    issues = checker.check_all()
    quotes_issues = [i for i in issues if i['type'] == 'quotes']
    assert len(quotes_issues) == 1
    assert "Mélange" in quotes_issues[0]['message']