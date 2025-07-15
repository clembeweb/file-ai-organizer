import pytesseract
from PIL import Image
from pathlib import Path
import math
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import re


def extract_text(file_path: str) -> str:
    """Estrae testo dal file specificato usando OCR o lettura diretta."""
    file_path = Path(file_path)
    text = ""
    try:
        if file_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img, lang='eng')
        elif file_path.suffix.lower() in [".txt", ".md"]:
            text = file_path.read_text(errors='ignore')
    except Exception as e:
        print(f"Errore durante extract_text su {file_path}: {e}")
    return text.strip()

model = None

def cluster_texts(texts: dict) -> dict:
    """Esegue embedding dei testi e clusterizza in gruppi similari."""
    global model
    if model is None:
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    if not texts:
        return {}
    file_paths = list(texts.keys())
    text_list = list(texts.values())
    embeddings = model.encode(text_list, show_progress_bar=False)
    embeddings = np.array(embeddings, dtype='float32')
    n = embeddings.shape[0]
    if n < 2:
        return {fp: 0 for fp in file_paths}
    num_clusters = max(2, int(math.sqrt(n)))
    kmeans = faiss.Kmeans(d=embeddings.shape[1], k=num_clusters, niter=20, verbose=False)
    kmeans.train(embeddings)
    distances, assignments = kmeans.index.search(embeddings, 1)
    clusters = [int(c[0]) for c in assignments]
    return {file_paths[i]: clusters[i] for i in range(n)}


def suggest_filename(text: str, file_path: str) -> str:
    """Genera un nome file suggerito basandosi sul contenuto testuale."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        base = lines[0]
    else:
        base = Path(file_path).stem
    base = base[:50]
    base = re.sub(r'[\\/*?:"<>|]', '', base).strip()
    if not base:
        base = 'file'
    new_name = base + Path(file_path).suffix.lower()
    return new_name
