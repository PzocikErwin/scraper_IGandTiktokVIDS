from sentence_transformers import SentenceTransformer, util
import numpy as np
from config import EMBEDDING_MODEL

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        print(f"Cargando modelo de embeddings '{EMBEDDING_MODEL}'...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def compute_embedding(text):
    """
    Computes the vector embedding for the given text.
    Returns a numpy array.
    """
    model = get_embedding_model()
    return model.encode(text)

def search_videos(query, stored_videos, top_k=5):
    """
    Searches through stored_videos for the best matches to query.
    stored_videos is a list of tuples: (id, platform, url, title, transcript, embedding_json)
    """
    if not stored_videos:
        return []
        
    model = get_embedding_model()
    query_emb = model.encode(query)
    
    results = []
    for video in stored_videos:
        vid, platform, url, title, transcript, embedding_json = video
        import json
        try:
            doc_emb = np.array(json.loads(embedding_json), dtype=np.float32)
            # Compute cosine similarity
            score = util.cos_sim(query_emb, doc_emb).item()
            results.append({
                "id": vid,
                "platform": platform,
                "url": url,
                "title": title,
                "transcript": transcript,
                "score": score
            })
        except Exception as e:
            print(f"Error procesando video {vid}: {e}")
            continue
            
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
