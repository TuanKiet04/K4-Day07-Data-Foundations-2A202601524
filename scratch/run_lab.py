import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath('.'))

from src.embeddings import MockEmbedder
from src.chunking import RecursiveChunker, compute_similarity
from src.agent import KnowledgeBaseAgent
from src.store import EmbeddingStore
from src import Document
import csv
import json

# ================================
# Section 4: Similarity
# ================================
pairs = [
    ("Tôi muốn đổi trả hàng", "Làm sao để hoàn trả sản phẩm", "cao"),
    ("Bao lâu thì nhận được hàng?", "Thời gian giao hàng là bao nhiêu ngày?", "cao"),
    ("Chính sách bảo mật thông tin", "Làm thế nào để thanh toán bằng thẻ tín dụng?", "thấp"),
    ("Tôi muốn mua điện thoại iPhone", "Cách liên hệ tổng đài chăm sóc khách hàng", "thấp"),
    ("Shopee có miễn phí vận chuyển không", "Phí ship trên Shopee tính thế nào", "cao")
]

embed_model = MockEmbedder()
print("--- SECTION 4 ---")
for i, (a, b, pred) in enumerate(pairs, 1):
    emb_a = embed_model(a)
    emb_b = embed_model(b)
    sim = compute_similarity(emb_a, emb_b)
    print(f"Pair {i}: A='{a}' | B='{b}' | Pred={pred} | Real={sim:.4f}")

# ================================
# Section 5: Retrieval
# ================================
print("\n--- SECTION 5 ---")

docs = []
# Create dummy documents mimicking the URLs since we don't have the real scraper output loaded right now
docs.append(Document(id="doc1", content="Shopee cam kết bảo vệ thông tin cá nhân của bạn. Người mua có thể yêu cầu trả hàng/hoàn tiền trong vòng 15 ngày kể từ khi nhận hàng. Phí vận chuyển sẽ được tính dựa trên khoảng cách.", metadata={"source": "shopee"}))
docs.append(Document(id="doc2", content="Tiki bảo mật thông tin người dùng bằng mã hóa. Bạn có thể thanh toán bằng thẻ tín dụng, ví điện tử MoMo, hoặc COD. Tiki thu thập họ tên, địa chỉ, số điện thoại để giao hàng.", metadata={"source": "tiki"}))
docs.append(Document(id="doc3", content="Thời gian giao hàng của Lazada phụ thuộc vào khu vực, thường từ 2-5 ngày làm việc. Người bán phải tuân thủ nghiêm ngặt các quy định về chất lượng sản phẩm.", metadata={"source": "lazada"}))

store = EmbeddingStore(collection_name="test_col", embedding_fn=embed_model)
store.add_documents(docs)

agent = KnowledgeBaseAgent(store=store, llm_fn=lambda p: "Dummy answer based on context")

queries = [
    "Làm thế nào để đổi trả hàng trên Shopee?",
    "Tiki thu thập những thông tin cá nhân nào của khách hàng?",
    "Quy định về thời gian giao hàng của Lazada là gì?",
    "Shopee bảo vệ thông tin người dùng như thế nào?",
    "Tôi có thể thanh toán trên Tiki bằng những phương thức nào?"
]

for i, q in enumerate(queries, 1):
    chunks = store.search(q, top_k=3)
    if chunks:
        top_chunk = chunks[0]['content']
        score = chunks[0]['score']
    else:
        top_chunk = ""
        score = 0
    ans = agent.answer(q)
    print(f"Q{i}: {q}")
    print(f"Top 1 Chunk: {top_chunk}")
    print(f"Score: {score:.4f}")
    print(f"Ans: {ans}")
    print("-" * 20)
