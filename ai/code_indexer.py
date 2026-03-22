# ai/code_indexer.py
import pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from ai.data_loader import load_aceob_data

class CodeOptimizationIndexer:
    def __init__(self, data_dir="data/ACEOB/ACEOB", split="train", sample_size=5000, rebuild=False):
        self.data_dir = data_dir
        self.split = split
        self.sample_size = sample_size
        self.inefficient_codes = []
        self.efficient_codes = []
        self.vectorizer = None
        self.vectors = None
        self.nn = None
        self.index_file = "code_index.pkl"

        if rebuild or not Path(self.index_file).exists():
            self._build_index()
        else:
            self._load_index()

    def _build_index(self):
        print(f"Construction de l'index à partir de {self.sample_size} paires...")
        data = load_aceob_data(self.data_dir, self.split, self.sample_size)
        if not data:
            raise ValueError("Aucune donnée chargée.")
        self.inefficient_codes = [item["inefficient_code"] for item in data]
        self.efficient_codes = [item["efficient_code"] for item in data]

        print("Vectorisation...")
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            lowercase=True,
            strip_accents='unicode'
        )
        self.vectors = self.vectorizer.fit_transform(self.inefficient_codes)

        print("Construction de l'index de voisins...")
        self.nn = NearestNeighbors(n_neighbors=3, metric='cosine')
        self.nn.fit(self.vectors)

        self._save_index()

    def _save_index(self):
        with open(self.index_file, "wb") as f:
            pickle.dump({
                "inefficient_codes": self.inefficient_codes,
                "efficient_codes": self.efficient_codes,
                "vectorizer": self.vectorizer,
                "vectors": self.vectors,
                "nn": self.nn
            }, f)
        print(f"Index sauvegardé dans {self.index_file}")

    def _load_index(self):
        try:
            with open(self.index_file, "rb") as f:
                data = pickle.load(f)
            self.inefficient_codes = data["inefficient_codes"]
            self.efficient_codes = data["efficient_codes"]
            self.vectorizer = data["vectorizer"]
            self.vectors = data["vectors"]
            self.nn = data["nn"]
            print(f"Index chargé : {len(self.inefficient_codes)} paires")
        except Exception as e:
            print(f"Erreur de chargement : {e}. Reconstruction...")
            self._build_index()

    def suggest_optimization(self, code, top_k=3):
        if not self.vectorizer:
            raise ValueError("Index non initialisé")
        code_vec = self.vectorizer.transform([code])
        distances, indices = self.nn.kneighbors(code_vec, n_neighbors=top_k)
        suggestions = []
        for i, idx in enumerate(indices[0]):
            similarity = 1 - distances[0][i]
            suggestions.append({
                "inefficient": self.inefficient_codes[idx][:500],
                "efficient": self.efficient_codes[idx][:500],
                "similarity": similarity
            })
        return suggestions