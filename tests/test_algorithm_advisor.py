import pytest
from core.parser import CodeParser
from knowledge.algorithm_advisor import AlgorithmAdvisor

@pytest.fixture
def sample_file_with_bubble_sort(tmp_path):
    content = """
def trier_liste(liste):
    n = len(liste)
    for i in range(n):
        for j in range(0, n-i-1):
            if liste[j] > liste[j+1]:
                liste[j], liste[j+1] = liste[j+1], liste[j]
    return liste
"""
    filepath = tmp_path / "bubble.py"
    filepath.write_text(content)
    return filepath

@pytest.fixture
def sample_file_with_linear_search(tmp_path):
    content = """
def chercher(liste, cible):
    for element in liste:
        if element == cible:
            return True
    return False
"""
    filepath = tmp_path / "linear.py"
    filepath.write_text(content)
    return filepath

def test_detect_bubble_sort(sample_file_with_bubble_sort):
    parser = CodeParser(str(sample_file_with_bubble_sort))
    advisor = AlgorithmAdvisor(parser)
    issues = advisor.analyze()
    assert len(issues) == 1
    assert issues[0]['pattern'] == 'tri_bulle'
    assert issues[0]['line'] == 2  # ligne de 'def trier_liste'

def test_detect_linear_search(sample_file_with_linear_search):
    parser = CodeParser(str(sample_file_with_linear_search))
    advisor = AlgorithmAdvisor(parser)
    issues = advisor.analyze()
    assert len(issues) == 1
    assert issues[0]['pattern'] == 'recherche_lineaire'

def test_no_false_positive(tmp_path):
    content = """
def bonne_fonction():
    x = 1 + 2
    return x
"""
    filepath = tmp_path / "ok.py"
    filepath.write_text(content)
    parser = CodeParser(str(filepath))
    advisor = AlgorithmAdvisor(parser)
    issues = advisor.analyze()
    assert len(issues) == 0