# ai/classifier.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from typing import List, Tuple, Dict
import os

# Définir les labels possibles (doivent correspondre à ceux utilisés dans l'entraînement)
LABELS = ["bubble_sort", "linear_search", "binary_search", "quick_sort"]

class CodeClassifier:
    def __init__(self, model_name: str = "microsoft/codebert-base", num_labels: int = len(LABELS), device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
        self.model.to(self.device)
        self.model.eval()

    def predict(self, code_snippet: str, threshold: float = 0.5) -> List[Tuple[str, float]]:
        """Retourne une liste de (label, score) pour les labels avec score > threshold."""
        inputs = self.tokenizer(code_snippet, return_tensors="pt", truncation=True, max_length=512, padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.sigmoid(logits).cpu().numpy()[0]  # pour multi-label
        predictions = []
        for i, p in enumerate(probs):
            if p > threshold:
                predictions.append((LABELS[i], float(p)))
        return predictions

    def fine_tune(self, train_data, val_data, output_dir="./fine_tuned_model"):
        """Fine-tuning du modèle sur un jeu de données (à implémenter)."""
        # TODO: utiliser datasets et Trainer
        pass