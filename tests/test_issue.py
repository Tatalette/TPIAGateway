# tests/test_issue.py
from core.issue import Issue

def test_issue_creation():
    issue = Issue(line=42, issue_type='test', message="Ceci est un test", suggestion="Faites ceci")
    assert issue.line == 42
    assert issue.type == 'test'
    assert issue.message == "Ceci est un test"
    assert issue.suggestion == "Faites ceci"
    assert issue.extra == {}

def test_issue_with_extra():
    issue = Issue(line=10, issue_type='naming', message="Mauvais nom", subtype='snake_case', symbol='maVariable')
    assert issue.extra['subtype'] == 'snake_case'
    assert issue.extra['symbol'] == 'maVariable'

def test_to_dict():
    issue = Issue(line=5, issue_type='warning', message="Attention", suggestion="Corrigez")
    d = issue.to_dict()
    assert d == {'line': 5, 'type': 'warning', 'message': 'Attention', 'suggestion': 'Corrigez'}

def test_to_dict_with_extra():
    issue = Issue(line=0, issue_type='global', message="Problème global", extra_info="info")
    d = issue.to_dict()
    assert d['extra_info'] == 'info'
    assert 'suggestion' not in d