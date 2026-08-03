import os
import sys

sys.path.insert(0, os.path.abspath('.'))

from src.chunking import ChunkingStrategyComparator, SentenceChunker, FixedSizeChunker, RecursiveChunker
from src.embeddings import OpenAIEmbedder
from src.agent import KnowledgeBaseAgent
from src.store import EmbeddingStore
from ingest import build_knowledge_base
from dotenv import load_dotenv

load_dotenv()

docs_dir = "data/my_docs"
print("Running Baseline comparison...")
comp = ChunkingStrategyComparator()
baseline_res = comp.compare(docs_dir)
print(baseline_res)

embedder = OpenAIEmbedder()

# Setup 3 different chunkers for 3 members
chunkers = {
    "TV1 (Sentence)": SentenceChunker(),
    "TV2 (Fixed 500)": FixedSizeChunker(chunk_size=500, chunk_overlap=50),
    "TV3 (Recursive 300)": RecursiveChunker(chunk_size=300)
}

queries = [
    "Làm sao để trả hàng trên Shopee?",
    "Thời gian xử lý hoàn tiền của Shopee là bao lâu?",
    "Tiki thu thập thông tin khách hàng để làm gì?",
    "Hàng dễ vỡ có được vận chuyển không?",
    "Đăng bán hàng giả có bị phạt không?"
]

results = {q: {} for q in queries}

for name, chunker in chunkers.items():
    print(f"\nEvaluating {name}...")
    store = build_knowledge_base(docs_dir, embedding_fn=embedder)
    # Re-chunk with the specific chunker? Wait, build_knowledge_base in ingest.py uses RecursiveChunker by default.
    # To use a custom chunker, I need to read the docs myself.
    pass

# Actually let's just do it manually
from src.parsers import MarkdownParser
from pathlib import Path

docs = []
for p in Path(docs_dir).glob("*.md"):
    with open(p, encoding="utf-8") as f:
        docs.extend(MarkdownParser().parse(f.read(), source=str(p)))

for name, chunker in chunkers.items():
    store = EmbeddingStore(collection_name=f"test_{name}", embedding_fn=embedder)
    store.add_documents(docs, chunker=chunker)
    for q in queries:
        chunks = store.search(q, top_k=1)
        if chunks:
            results[q][name] = chunks[0]['score']
        else:
            results[q][name] = 0.0

import pprint
pprint.pprint(results)
