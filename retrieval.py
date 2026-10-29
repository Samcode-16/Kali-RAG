import re
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from rank_bm25 import BM25Okapi

THRESHOLD = 0.35
USE_TITLE = True
DOCS_DIR = "data/raw/kali-docs"

def get_title(text):
    m = re.search(r'^title:\s*(.+)$', text, re.M)
    return m.group(1).strip().strip('"') if m else ""

def pack_paragraphs(text, max_words=150):
    paras = [p for p in text.split("\n\n") if p.strip()]
    out, cur, n = [], [], 0
    for p in paras:
        w = len(p.split())
        if cur and n + w > max_words:
            out.append("\n\n".join(cur))
            cur, n = [], 0
        cur.append(p)
        n += w
    if cur:
        out.append("\n\n".join(cur))
    return out

def tok(s):
    return re.findall(r"\w+", s.lower())

chunks = []
for f in Path(DOCS_DIR).rglob("*.md"):
    text = f.read_text(encoding="utf-8", errors="ignore")
    if 'archived: "true"' in text:
        continue
    title = get_title(text)
    for part in text.split("\n## "):
        heading = part.split("\n", 1)[0][:80]
        for piece in pack_paragraphs(part):
            if len(piece) > 100:
                label = f"{f.parent.name} | {title} | {heading}" if USE_TITLE else f"{f.parent.name} | {heading}"
                chunks.append((f.parent.name, label + "\n" + piece))

# TEMPORARY DIAGNOSTIC
print("\nChecking indexed chunks for Kali key-recovery instructions:")

for i, (folder, text) in enumerate(chunks):
    if "archive-keyring.gpg" in text.lower() or "kali-archive-keyring" in text.lower():
        print(f"\nChunk {i} | Folder: {folder}")
        print(text[:1000])

model = SentenceTransformer("all-MiniLM-L6-v2")
vecs = model.encode([c[1] for c in chunks])
bm25 = BM25Okapi([tok(c[1]) for c in chunks])

def hybrid_top(question, k=3):
    dense = util.cos_sim(model.encode(question), vecs)[0]
    best_dense = float(dense.max())
    dense_rank = dense.argsort(descending=True).tolist()
    bm = bm25.get_scores(tok(question))
    bm_rank = sorted(range(len(bm)), key=lambda i: -bm[i])
    fused = {}
    for rank_list in (dense_rank, bm_rank):
        for r, i in enumerate(rank_list[:50]):
            fused[i] = fused.get(i, 0) + 1 / (60 + r)
    ranked = sorted(fused, key=fused.get, reverse=True)
    
    top = []
    folder_counts = {}

    for i in ranked:
        folder = chunks[i][0]

        # Allow up to 2 relevant chunks per document folder.
        if folder_counts.get(folder, 0) >= 3:
            continue

        folder_counts[folder] = folder_counts.get(folder, 0) + 1
        top.append(i)

        if len(top) == k:
            break

    return best_dense, top
