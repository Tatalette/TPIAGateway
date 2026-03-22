import pickle
import numpy as np
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer
from ai.data_loader import load_aceob_data

class CodeOptimizationIndexer:
    def __init__(self, data_dir="data/ACEOB/ACEOB", split="train", sample_size=5000, rebuild=False):
        self.data_dir = data_dir
        self.split = split
        self.sample_size = sample_size
        self.inefficient_codes = []
        self.efficient_codes = []
        self.model = None
        self.embeddings = None
        self.index = None
        self.index_file = "code_index_faiss.pkl"

        # Charger ou construire l'index
        if rebuild or not Path(self.index_file).exists():
            self._build_index()
        else:
            self._load_index()

    def _build_index(self):
        print(f"Construction de l'index FAISS avec {self.sample_size} paires...")
        data = load_aceob_data(self.data_dir, self.split, self.sample_size)
        if not data:
            raise ValueError("Aucune donnée chargée.")
        self.inefficient_codes = [item["inefficient_code"] for item in data]
        self.efficient_codes = [item["efficient_code"] for item in data]

        print("Chargement du modèle SentenceTransformer (CodeBERT)...")
        self.model = SentenceTransformer('microsoft/codebert-base')
        print("Calcul des embeddings...")
        # CodeBERT attend des phrases, on peut donner le code tel quel
        self.embeddings = self.model.encode(self.inefficient_codes, show_progress_bar=True, convert_to_numpy=True)

        print("Création de l'index FAISS (IP) et normalisation...")
        # Normalisation pour similarité cosinus (FAISS IP après L2 norm)
        faiss.normalize_L2(self.embeddings)
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # produit scalaire = cosinus après normalisation
        self.index.add(self.embeddings)
        print(f"Index construit avec {self.index.ntotal} vecteurs.")

        self._save_index()

    def _save_index(self):
        with open(self.index_file, "wb") as f:
            pickle.dump({
                "inefficient_codes": self.inefficient_codes,
                "efficient_codes": self.efficient_codes,
                "embeddings": self.embeddings,
                "index": self.index,
                "model_name": "microsoft/codebert-base"
            }, f)
        print(f"Index sauvegardé dans {self.index_file}")

    def _load_index(self):
        try:
            with open(self.index_file, "rb") as f:
                data = pickle.load(f)
            self.inefficient_codes = data["inefficient_codes"]
            self.efficient_codes = data["efficient_codes"]
            self.embeddings = data["embeddings"]
            self.index = data["index"]
            self.model = SentenceTransformer(data["model_name"])
            print(f"Index chargé : {len(self.inefficient_codes)} paires")
        except Exception as e:
            print(f"Erreur de chargement : {e}. Reconstruction...")
            self._build_index()

    def suggest_optimization(self, code, top_k=3):
        if not self.model or not self.index:
            raise ValueError("Index non initialisé")
        # Encoder le code
        query_emb = self.model.encode([code], convert_to_numpy=True)
        faiss.normalize_L2(query_emb)
        distances, indices = self.index.search(query_emb, top_k)
        suggestions = []
        for i, idx in enumerate(indices[0]):
            similarity = float(distances[0][i])
            suggestions.append({
                "inefficient": self.inefficient_codes[idx][:500],
                "efficient": self.efficient_codes[idx][:500],
                "similarity": similarity
            })
        return suggestions