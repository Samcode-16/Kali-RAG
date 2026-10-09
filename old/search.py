from pathlib import Path
from sentence_transformers import SentenceTransformer, util

THRESHOLD = 0.40   # below this score = "I don't know"

chunks = []
for f in Path("data/raw/kali-docs").rglob("*.md"):
    text = f.read_text(encoding="utf-8", errors="ignore")
    if 'archived: "true"' in text:        # skip outdated pages
        continue
    title = f.parent.name                  # e.g. install-virtualbox-guest-vm
    for part in text.split("\n## "):
        if len(part) > 200:
            chunks.append((str(f), title + "\n" + part))

print("Loaded", len(chunks), "chunks. Building index...")
model = SentenceTransformer("all-MiniLM-L6-v2")
vecs = model.encode([c[1] for c in chunks])

while True:
    question = input("\nAsk a Kali question (or type quit): ")
    if question.strip().lower() == "quit":
        break
    q = model.encode(question)
    hits = util.cos_sim(q, vecs)[0].topk(3)

    best = float(hits.values[0])
    if best < THRESHOLD:
        print(f"I don't know (best score {best:.2f}). Closest was:")
        print("  ", chunks[hits.indices[0]][0])
        continue

    for score, i in zip(hits.values, hits.indices):
        if float(score) < THRESHOLD:
            continue
        path, text = chunks[i]
        print("=" * 60)
        print("FILE :", path)
        print("SCORE:", round(float(score), 2))
        print(text[:600])