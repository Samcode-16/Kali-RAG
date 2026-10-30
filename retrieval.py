
import re
from pathlib import Path

from sentence_transformers import SentenceTransformer, util
from rank_bm25 import BM25Okapi


# Configuration
THRESHOLD = 0.35
CHUNK_SIZE = 150
OVERLAP_PARAGRAPHS = 1
RRF_K = 60
SEARCH_DEPTH = 50

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "data" / "raw" / "kali-docs"


# Extract YAML title
def get_title(text):
    match = re.search(
        r"^title:\s*[\"']?(.+?)[\"']?\s*$",
        text,
        re.MULTILINE
    )
    return match.group(1).strip() if match else ""


# Remove YAML front matter
def remove_frontmatter(text):
    return re.sub(
        r"\A---\s*\n.*?\n---\s*\n",
        "",
        text,
        count=1,
        flags=re.DOTALL
    )


# Extract Markdown sections
def extract_sections(text):
    lines = text.splitlines()

    sections = []
    current_heading = "Introduction"
    current_content = []

    for line in lines:
        match = re.match(r"^(#{1,6})\s+(.+)", line)

        if match:
            if current_content:
                sections.append(
                    (current_heading, "\n".join(current_content))
                )

            current_heading = match.group(2).strip()
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections.append(
            (current_heading, "\n".join(current_content))
        )

    return sections


# Split large paragraphs into smaller pieces
def split_long_paragraph(paragraph, max_words):
    words = paragraph.split()

    if len(words) <= max_words:
        return [paragraph]

    return [
        " ".join(words[i:i + max_words])
        for i in range(0, len(words), max_words)
    ]


# Create overlapping chunks
def pack_paragraphs(text, max_words=CHUNK_SIZE):
    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    pieces = []

    for paragraph in paragraphs:
        pieces.extend(
            split_long_paragraph(paragraph, max_words)
        )

    chunks = []
    current = []
    word_count = 0

    for piece in pieces:
        piece_words = len(piece.split())

        if current and word_count + piece_words > max_words:
            chunks.append("\n\n".join(current))

            current = current[-OVERLAP_PARAGRAPHS:]
            word_count = sum(len(p.split()) for p in current)

        current.append(piece)
        word_count += piece_words

    if current:
        chunks.append("\n\n".join(current))

    return chunks


# Tokenization for BM25
def tok(text):
    return re.findall(
        r"[a-zA-Z0-9_./+-]+",
        text.lower()
    )


# Load documents
def load_documents():
    if not DOCS_DIR.exists():
        raise RuntimeError(
            f"Kali docs directory not found: {DOCS_DIR}"
        )

    md_files = sorted(DOCS_DIR.rglob("*.md"))

    if not md_files:
        raise RuntimeError("No Markdown files found.")

    loaded_chunks = []

    for file in md_files:
        raw_text = file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        if re.search(
            r'^archived:\s*["\']?true["\']?\s*$',
            raw_text,
            re.MULTILINE
        ):
            continue

        title = get_title(raw_text)
        body = remove_frontmatter(raw_text)

        for heading, section_text in extract_sections(body):
            for piece in pack_paragraphs(section_text):

                if len(piece.strip()) < 30:
                    continue

                document = file.parent.name

                metadata = (
                    f"Document: {document}\n"
                    f"Title: {title}\n"
                    f"Section: {heading}\n"
                )

                searchable_text = metadata + "\n" + piece

                loaded_chunks.append({
                    "folder": document,
                    "title": title,
                    "heading": heading,
                    "text": searchable_text,
                    "content": piece
                })

    if not loaded_chunks:
        raise RuntimeError("No usable chunks were created.")

    return loaded_chunks


# Initialize the document collection
chunks = load_documents()

print("Docs directory:", DOCS_DIR)
print("Markdown files:", len(list(DOCS_DIR.rglob("*.md"))))
print("Number of chunks:", len(chunks))


# Initialize embedding model and BM25
model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [chunk["text"] for chunk in chunks]

vecs = model.encode(
    texts,
    convert_to_tensor=True,
    normalize_embeddings=True
)

bm25 = BM25Okapi([
    tok(text)
    for text in texts
])


# Retrieve dense and BM25 rankings
def get_rankings(question):
    query_vector = model.encode(
        question,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    dense_scores = util.cos_sim(query_vector, vecs)[0]

    dense_rank = dense_scores.argsort(
        descending=True
    ).tolist()

    bm25_scores = bm25.get_scores(tok(question))

    bm25_rank = sorted(
        range(len(bm25_scores)),
        key=lambda i: bm25_scores[i],
        reverse=True
    )

    return dense_scores, dense_rank, bm25_scores, bm25_rank


# Reciprocal Rank Fusion
def fuse_rankings(dense_rank, bm25_rank):
    fused = {}

    for rank_list in (dense_rank, bm25_rank):
        for rank, index in enumerate(rank_list[:SEARCH_DEPTH]):
            fused[index] = fused.get(index, 0) + (
                1 / (RRF_K + rank + 1)
            )

    return sorted(
        fused,
        key=lambda i: fused[i],
        reverse=True
    ), fused


# Main retrieval function
def hybrid_top(question, k=5):
    dense_scores, dense_rank, bm25_scores, bm25_rank = (
        get_rankings(question)
    )

    best_dense = float(dense_scores.max())

    ranked, fused_scores = fuse_rankings(
        dense_rank,
        bm25_rank
    )

    top = ranked[:k]

    return best_dense, top


# Diagnostic function
def debug_retrieval(question, k=10):
    dense_scores, dense_rank, bm25_scores, bm25_rank = (
        get_rankings(question)
    )

    ranked, fused_scores = fuse_rankings(
        dense_rank,
        bm25_rank
    )

    def display(label, indices, scores):
        print(f"\n========== {label} ==========")

        for rank, index in enumerate(indices[:k], 1):
            chunk = chunks[index]

            print(f"\nRank: {rank}")
            print(f"Score: {scores[index]:.4f}")
            print(f"Document: {chunk['folder']}")
            print(f"Title: {chunk['title']}")
            print(f"Section: {chunk['heading']}")
            print(f"Content: {chunk['content'][:500]}")

    display(
        "DENSE SEARCH",
        dense_rank,
        dense_scores
    )

    display(
        "BM25 SEARCH",
        bm25_rank,
        bm25_scores
    )

    display(
        "HYBRID SEARCH",
        ranked,
        fused_scores
    )

    print("\n========== BEST DENSE SCORE ==========")
    print(f"{float(dense_scores.max()):.4f}")
