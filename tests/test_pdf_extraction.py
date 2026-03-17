# tests/test_pdf_extraction.py
import pytest
from knowledge.pdf_extractor import extract_blocks
from knowledge.nlp_extractor import extract_algorithm_info

def test_extract_blocks():
    # Utilisez un vrai PDF ou créez un mock
    blocks = extract_blocks("tests/sample.pdf")
    assert isinstance(blocks, list)

def test_nlp_extraction():
    text = "L'algorithme de tri rapide a une complexité O(n log n)."
    info = extract_algorithm_info(text)
    assert "tri rapide" in info["entities"] or "tri" in info["keywords"]
    assert len(info["complexities"]) > 0