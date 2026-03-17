# tests/test_pdf_extraction.py
import pytest
from knowledge.pdf_extractor import extract_blocks
from knowledge.nlp_extractor import extract_algorithm_info

def test_complexity_regex():
    text = "O(n log n) et O(n^2)"
    import re
    pattern = r'O\s*\([^)]+\)'
    matches = re.findall(pattern, text, re.IGNORECASE)
    assert len(matches) == 2
    assert matches[0] == "O(n log n)"

def test_extract_blocks():
    # Utilisez un vrai PDF ou créez un mock
    blocks = extract_blocks("tests/test_pdf.pdf")
    assert isinstance(blocks, list)

def test_nlp_extraction():
    text = "L'algorithme de tri rapide a une complexité O(n log n)."
    info = extract_algorithm_info(text)
    print("Keywords:", info["keywords"])
    print("Complexities:", info["complexities"])
    print("Entities:", info["entities"])
    assert "tri" in info["keywords"] or "rapide" in info["keywords"]
    assert len(info["complexities"]) > 0