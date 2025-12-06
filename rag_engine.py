# rag_engine.py (versi aman untuk Streamlit Cloud)
import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RAG")

# Load model (cache di memori)
_model = None
_index = None
_documents = None

def get_model():
    global _model
    if _model is None:
        logger.info("✅ Loading sentence-transformers model...")
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _model

def build_index():
    global _index, _documents
    data_path = "data/knowledge_blitar.json"
    cache_path = "data/embedding_cache.pkl"

    # Force rebuild if in Streamlit Cloud
    if os.getenv("STREAMLIT_CLOUD", "0") == "1":
        logger.warning("⚠️ Running in Streamlit Cloud — forcing index rebuild")
        if os.path.exists(cache_path):
            os.remove(cache_path)

    # Coba baca cache
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'rb') as f:
                cache = pickle.load(f)
                _index = cache['index']
                _documents = cache['docs']
                logger.info("✅ Cache embedding dimuat dari %s", cache_path)
                return
        except Exception as e:
            logger.error("❌ Cache rusak: %s. Membuat ulang...", str(e))
            os.remove(cache_path)

    # Jika cache tidak ada/rusak → buat ulang
    if not os.path.exists(data_path):
        logger.error("❌ Knowledge base tidak ditemukan: %s", data_path)
        raise FileNotFoundError("File knowledge_blitar.json tidak ada")

    with open(data_path, 'r', encoding='utf-8') as f:
        docs = json.load(f)
    logger.info("📚 Memuat %d entri knowledge base", len(docs))

    model = get_model()
    texts = [d['konten'] for d in docs]
    
    # Encode dengan error handling
    try:
        embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    except Exception as e:
        logger.error("❌ Gagal encode teks: %s", str(e))
        raise

    dim = embeddings.shape[1]
    logger.info("🔧 Membuat FAISS index dengan dimensi %d", dim)
    
    # Gunakan IndexFlatIP untuk cosine similarity
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)  # Penting untuk cosine similarity
    index.add(embeddings.astype('float32'))

    _index = index
    _documents = docs

    # Simpan cache
    with open(cache_path, 'wb') as f:
        pickle.dump({'index': index, 'docs': docs}, f)
    logger.info("✅ Cache embedding baru disimpan ke %s", cache_path)

def retrieve(query: str, top_k: int = 3):
    """Cari dokumen paling relevan dari knowledge base."""
    if _index is None or _documents is None:
        logger.info("🔍 Index belum ada — membangun ulang...")
        build_index()

    try:
        model = get_model()
        query_vec = model.encode([query], normalize_embeddings=True).astype('float32')
        faiss.normalize_L2(query_vec)  # Normalisasi untuk cosine similarity
        
        # Pastikan query_vec dalam bentuk 2D array
        if query_vec.ndim == 1:
            query_vec = np.expand_dims(query_vec, axis=0)
        
        # Cari dengan FAISS
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
    except Exception as e:
        logger.exception("❌ Error saat retrieve: %s", str(e))
        return []