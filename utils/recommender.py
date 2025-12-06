# utils/recommender.py
import json
import os
from collections import Counter

# Load knowledge sekali
_knowledge = None

def _load_kb():
    global _knowledge
    if _knowledge is None:
        with open("data/knowledge_blitar.json", 'r', encoding='utf-8') as f:
            _knowledge = json.load(f)
    return _knowledge

def recommend(kategori: str, tags: list, top_n: int = 2) -> list:
    """Rekomendasi berdasar kategori & tag — rule-based sederhana."""
    kb = _load_kb()
    
    # Skor berdasar: kategori cocok + jumlah tag overlap
    scored = []
    for doc in kb:
        score = 0
        if doc["kategori"] == kategori:
            score += 2
        overlap = len(set(tags) & set(doc.get("tag", [])))
        score += overlap
        if score > 0:
            scored.append((doc["judul"], score))
    
    # Urut & ambil top
    scored.sort(key=lambda x: x[1], reverse=True)
    titles = [item[0] for item in scored[:top_n]]
    return titles