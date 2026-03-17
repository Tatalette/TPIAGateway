import pytest
from pathlib import Path
from core.parser import CodeParser

# Créons un fichier temporaire pour les tests
@pytest.fixture
def sample_py_file(tmp_path):
    content = """
# Ceci est un commentaire
def ma_fonction():
    x = 1
    return x

class MaClasse:
    def __init__(self):
        self.attr = 2
"""
    filepath = tmp_path / "sample.py"
    filepath.write_text(content)
    return filepath

def test_parser_initialization(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    assert parser.filepath == sample_py_file
    assert parser.source is not None

def test_get_functions(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    funcs = parser.get_functions()
    assert len(funcs) == 2  # ma_fonction et __init__
    assert funcs[0].name == "ma_fonction"

def test_get_classes(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    classes = parser.get_classes()
    assert len(classes) == 1
    assert classes[0].name == "MaClasse"

def test_extract_comments(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    comments = parser.extract_comments()
    assert len(comments) == 1
    assert comments[0]['text'] == "# Ceci est un commentaire"

def test_get_all_names(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    names = parser.get_all_names()
    # On doit trouver : ma_fonction (fonction), x (variable), MaClasse (classe), __init__ (fonction), self (param), attr (variable)
    # Le comptage exact peut varier selon la représentation AST, on teste juste la présence
    func_names = [n['id'] for n in names if n.get('type') == 'function']
    class_names = [n['id'] for n in names if n.get('type') == 'class']
    assert "ma_fonction" in func_names
    assert "__init__" in func_names
    assert "MaClasse" in class_names