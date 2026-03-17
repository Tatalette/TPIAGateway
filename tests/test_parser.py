import pytest
import ast
from pathlib import Path
from core.parser import CodeParser

@pytest.fixture
def sample_py_file(tmp_path):
    content = """
# Ceci est un commentaire
def ma_fonction(x, y):
    \"\"\"Docstring de fonction.\"\"\"
    a = x + y
    return a

class MaClasse:
    def __init__(self):
        self.attr = 2

# Une compréhension
ma_liste = [i for i in range(10)]

import os
from sys import path as sys_path
"""
    filepath = tmp_path / "sample.py"
    filepath.write_text(content)
    return filepath

def test_parser_initialization(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    assert parser.filepath == sample_py_file
    assert parser.source is not None
    assert len(parser.lines) > 0

def test_parser_syntax_error(tmp_path):
    invalid_content = "def foo( :"  # SyntaxError volontaire
    filepath = tmp_path / "invalid.py"
    filepath.write_text(invalid_content)
    with pytest.raises(SyntaxError):
        CodeParser(str(filepath))

def test_get_functions(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    funcs = parser.get_functions()
    assert len(funcs) == 2  # ma_fonction et __init__
    names = [f.name for f in funcs]
    assert "ma_fonction" in names
    assert "__init__" in names

def test_get_classes(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    classes = parser.get_classes()
    assert len(classes) == 1
    assert classes[0].name == "MaClasse"

def test_get_imports(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    imports = parser.get_imports()
    assert len(imports) == 2  # import os, from sys import path as sys_path

def test_get_functions_detailed(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    details = parser.get_functions_detailed()
    assert len(details) == 2
    ma_fonction = next(d for d in details if d['name'] == 'ma_fonction')
    assert ma_fonction['lineno'] == 3
    assert ma_fonction['docstring'] == "Docstring de fonction."
    assert ma_fonction['args'] == ['x', 'y']

def test_get_all_names(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    names = parser.get_all_names()
    # Vérifions quelques noms importants
    ids = [n['id'] for n in names]
    assert "ma_fonction" in ids
    assert "x" in ids  # paramètre
    assert "y" in ids
    assert "a" in ids  # variable locale
    assert "MaClasse" in ids
    assert "__init__" in ids
    assert "attr" in ids  # attribut
    assert "i" in ids  # variable de compréhension
    assert "os" in ids  # import
    assert "sys_path" in ids  # alias d'import

def test_extract_comments(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    comments = parser.extract_comments()
    assert len(comments) == 2  # deux commentaires (ligne 2 et ligne 14)
    texts = [c['text'] for c in comments]
    assert "# Ceci est un commentaire" in texts
    assert "# Une compréhension" in texts

def test_get_string_tokens(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    tokens = parser.get_string_tokens()
    # Doit trouver la docstring (triple quotes) et peut-être d'autres chaînes (il n'y en a pas ici)
    # La docstring est un token STRING
    assert len(tokens) >= 1
    # On peut vérifier que le token contient la docstring
    docstring_found = any('Docstring de fonction' in tok.string for tok in tokens)
    assert docstring_found

def test_get_node_at_line(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    node = parser.get_node_at_line(3)  # ligne de def ma_fonction
    assert isinstance(node, ast.FunctionDef)
    assert node.name == "ma_fonction"

def test_get_lines(sample_py_file):
    parser = CodeParser(str(sample_py_file))
    lines = parser.get_lines(3, 5)
    assert len(lines) == 3
    assert lines[0] == 'def ma_fonction(x, y):'