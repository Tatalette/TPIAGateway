# tests/test_algorithm_advisor.py
import pytest
from core.parser import CodeParser
from knowledge.algorithm_advisor import AlgorithmAdvisor

@pytest.fixture
def sample_bubble_sort(tmp_path):
    content = """
def tri_bulle(liste):
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
def sample_linear_search(tmp_path):
    content = """
def recherche_lineaire(liste, cible):
    for element in liste:
        if element == cible:
            return True
    return False
"""
    filepath = tmp_path / "linear.py"
    filepath.write_text(content)
    return filepath

@pytest.fixture
def sample_binary_search(tmp_path):
    content = """
def recherche_binaire(liste, cible):
    gauche, droite = 0, len(liste)-1
    while gauche <= droite:
        milieu = (gauche + droite) // 2
        if liste[milieu] == cible:
            return True
        elif liste[milieu] < cible:
            gauche = milieu + 1
        else:
            droite = milieu - 1
    return False
"""
    filepath = tmp_path / "binary.py"
    filepath.write_text(content)
    return filepath

@pytest.fixture
def sample_quick_sort(tmp_path):
    content = """
def tri_rapide(liste):
    if len(liste) <= 1:
        return liste
    pivot = liste[0]
    petits = [x for x in liste[1:] if x <= pivot]
    grands = [x for x in liste[1:] if x > pivot]
    return tri_rapide(petits) + [pivot] + tri_rapide(grands)
"""
    filepath = tmp_path / "quicksort.py"
    filepath.write_text(content)
    return filepath

def test_detect_bubble_sort(sample_bubble_sort):
    parser = CodeParser(str(sample_bubble_sort))
    advisor = AlgorithmAdvisor(parser)
    issues = advisor.analyze()
    assert len(issues) == 1
    assert issues[0].extra['pattern'] == 'tri_bulle'

def test_detect_linear_search(sample_linear_search):
    parser = CodeParser(str(sample_linear_search))
    advisor = AlgorithmAdvisor(parser)
    issues = advisor.analyze()
    assert len(issues) == 1
    assert issues[0].extra['pattern'] == 'recherche_lineaire'

def test_detect_binary_search(sample_binary_search):
    parser = CodeParser(str(sample_binary_search))
    advisor = AlgorithmAdvisor(parser)
    issues = advisor.analyze()
    # On peut avoir plusieurs motifs détectés, mais au moins recherche dichotomique
    patterns = [i.extra['pattern'] for i in issues]
    assert 'recherche_dichotomique' in patterns

def test_detect_quick_sort(sample_quick_sort):
    parser = CodeParser(str(sample_quick_sort))
    advisor = AlgorithmAdvisor(parser)
    issues = advisor.analyze()
    patterns = [i.extra['pattern'] for i in issues]
    assert 'tri_rapide_maison' in patterns

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