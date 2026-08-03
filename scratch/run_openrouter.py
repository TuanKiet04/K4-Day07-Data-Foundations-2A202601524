import os
import sys

sys.path.insert(0, os.path.abspath('.'))

from src.chunking import compute_similarity
from src.agent import KnowledgeBaseAgent
from src.store import EmbeddingStore
from src import Document
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class OpenRouterEmbedder:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY")
        )
        self.model = os.environ.get("OPENAI_EMBEDDING_MODEL", "openai/text-embedding-3-small")
        # OpenRouter expects openai/ prefix for some models if using their standard routing
        if not self.model.startswith("openai/"):
            self.model = "openai/" + self.model

    def __call__(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.model, input=text)
        return [float(value) for value in response.data[0].embedding]

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

embed_model = OpenRouterEmbedder()
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

from ingest import build_knowledge_base
store = build_knowledge_base("data/my_docs", embedding_fn=embed_model)

agent = KnowledgeBaseAgent(store=store, llm_fn=lambda p: "Dummy answer based on context")

queries = [
    "Làm sao để trả hàng trên Shopee?",
    "Thời gian xử lý hoàn tiền của Shopee là bao lâu?",
    "Tiki thu thập thông tin khách hàng để làm gì?",
    "Hàng dễ vỡ có được vận chuyển không?",
    "Đăng bán hàng giả có bị phạt không?"
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
