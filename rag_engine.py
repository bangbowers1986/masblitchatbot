# rag_engine.py
import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle

# Load model (cache di memori)
_model = None
_index = None
_documents = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _model

def build_index():
    global _index, _documents
    data_path = "data/knowledge_blitar.json"
    cache_path = "data/embedding_cache.pkl"

    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            cache = pickle.load(f)
            _index = cache['index']
            _documents = cache['docs']
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        docs = json.load(f)

    model = get_model()
    texts = [d['konten'] for d in docs]
    embeddings = model.encode(texts, normalize_embeddings=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype('float32'))

    _index = index
    _documents = docs

    # Simpan cache
    with open(cache_path, 'wb') as f:
        pickle.dump({'index': index, 'docs': docs}, f)

def retrieve(query: str, top_k: int = 3):
    """Cari dokumen paling relevan dari knowledge base."""
    if _index is None or _documents is None:
        build_index()

    model = get_model()
    query_vec = model.encode([query], normalize_embeddings=True).astype('float32')
    distances, indices = _index.search(query_vec, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx == -1:
            continue
        doc = _documents[idx]
        score = float(distances[0][i])
        if score > 0.3:  # Threshold relevansi
            results.append({
                "id": doc["id"],
                "judul": doc["judul"],
                "konten": doc["konten"],
                "kategori": doc["kategori"],
                "tag": doc.get("tag", []),
                "score": score
            })
    return results