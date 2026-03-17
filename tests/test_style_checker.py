# tests/test_style_checker.py
import pytest
from core.parser import CodeParser
from core.style_checker import StyleChecker

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
    naming_issues = [i for i in issues if i.type == 'naming']
    assert len(naming_issues) == 3  # maClasse, attributVariable, MaFonction
    lines = [i.line for i in naming_issues]
    assert 2 in lines
    assert 4 in lines
    assert 6 in lines

def test_quotes_issues(sample_file_with_issues):
    parser = CodeParser(str(sample_file_with_issues))
    checker = StyleChecker(parser)
    issues = checker.check_all()
    quotes_issues = [i for i in issues if i.type == 'quotes']
    assert len(quotes_issues) == 1
    assert "Mélange" in quotes_issues[0].message

def test_trailing_whitespace(tmp_path):
    content = "def foo():\n    return 1  \n"
    filepath = tmp_path / "trailing.py"
    filepath.write_text(content)
    parser = CodeParser(str(filepath))
    checker = StyleChecker(parser)
    issues = checker.check_all()
    trailing = [i for i in issues if i.type == 'trailing_whitespace']
    assert len(trailing) == 1
    assert trailing[0].line == 2

def test_quotes_with_fstrings(tmp_path):
    content = 'a = "hello"\nb = f"world"\nc = \'!\''
    filepath = tmp_path / "fstrings.py"
    filepath.write_text(content)
    parser = CodeParser(str(filepath))
    checker = StyleChecker(parser)
    issues = checker.check_all()
    quotes = [i for i in issues if i.type == 'quotes']
    assert len(quotes) == 1  # mélange de " et '