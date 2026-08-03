# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> Tập trung vào quy định trả hàng/hoàn tiền, vận chuyển và chính sách bảo mật thông tin khách hàng của Shopee và Tiki.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | ĐIỀU KHOẢN DỊCH VỤ Shopee | https://help.shopee.vn/portal/4/article/77243 | 2026-08-03 | 111573 | `source_url`, `retrieved_at`, `license` |
| 2 | CHÍNH SÁCH BẢO MẬT Shopee | https://help.shopee.vn/portal/4/article/77244 | 2026-08-03 | 58097 | `source_url`, `retrieved_at`, `license` |
| 3 | Privacy Policy Tiki | https://tiki.vn/khuyen-mai/privacy-policy | 2026-08-03 | 10349 | `source_url`, `retrieved_at`, `license` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `source_url` | string | `https://help.shopee.vn...` | Giúp trích dẫn nguồn khi AI sinh câu trả lời, tăng độ tin cậy. |
| `retrieved_at` | string | `2026-08-03` | Giúp lọc ra các chính sách mới nhất nếu có nhiều phiên bản. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Shopee | FixedSizeChunker (`fixed_size`) | ~550 | 200 | Không (cắt ngang câu) |
| Shopee | SentenceChunker (`by_sentences`) | ~700 | 150 | Có (trọn vẹn câu) |
| Shopee | RecursiveChunker (`recursive`) | ~350 | 300 | Có (giữ được đoạn) |

### Chiến lược của từng thành viên

**Thành viên 1 — [Thành viên 1]**
- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn cho chủ đề này:** Dùng SentenceChunker cắt theo từng câu để đảm bảo không bị đứt gãy thông tin giữa chừng, rất phù hợp cho các câu hỏi cần tìm kiếm chi tiết nhỏ trong chính sách.

**Thành viên 2 — [Thành viên 2]**
- **Loại chiến lược:** FixedSizeChunker(chunk_size=300, chunk_overlap=50)
- **Mô tả & lý do chọn:** Độ dài cố định giúp dễ kiểm soát số lượng token đưa vào LLM. Có thêm overlap 50 ký tự để vớt vát lại các câu bị cắt ngang.

**Thành viên 3 — [Thành viên 3]**
- **Loại chiến lược:** RecursiveChunker(chunk_size=500, chunk_overlap=100)
- **Mô tả & lý do chọn:** Chủ đề chính sách có cấu trúc đoạn văn dài, dùng cắt đệ quy giúp bảo toàn ngữ cảnh tốt nhất theo các dấu xuống dòng và dấu chấm câu.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| TV1 | SentenceChunker | 6 | Tìm câu cực kỳ chính xác | Mất ngữ cảnh bao quát, AI khó hiểu |
| TV2 | FixedSizeChunker | 7 | Kích thước đều đặn | Vẫn bị đứt chữ ở đầu/cuối đoạn |
| TV3 | RecursiveChunker | 9 | Đoạn văn hoàn chỉnh, rõ ý | Tốn bộ nhớ hơn một chút |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> RecursiveChunker là chiến lược hiệu quả nhất. Lý do là các tài liệu chính sách (như Điều khoản dịch vụ của Shopee) thường được viết theo các đoạn văn dài giải thích ngữ cảnh. Việc cắt theo câu (Sentence) khiến AI không hiểu được câu đó áp dụng cho trường hợp nào, trong khi cắt cố định (Fixed) dễ làm mất ý. Cắt đệ quy bảo toàn được nguyên một khổ văn.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Làm sao để trả hàng trên Shopee? | Người mua cần tạo yêu cầu Trả hàng/Hoàn tiền trên ứng dụng Shopee. | Điều khoản dịch vụ Shopee |
| 2 | Thời gian xử lý hoàn tiền của Shopee là bao lâu? | Shopee sẽ chuyển khoản vào Tài khoản nhận tiền trong tối đa 4 ngày làm việc. | Điều khoản dịch vụ Shopee |
| 3 | Tiki thu thập thông tin khách hàng để làm gì? | Để xử lý đơn hàng, giao hàng, bảo mật và cung cấp dịch vụ tốt hơn. | Chính sách bảo mật Tiki |
| 4 | Hàng dễ vỡ có được vận chuyển không? | Có, nhưng người bán phải tuân thủ quy cách đóng gói đặc biệt của Shopee. | Điều khoản dịch vụ Shopee |
| 5 | Đăng bán hàng giả có bị phạt không? | Có, Shopee sẽ xóa sản phẩm, khóa tài khoản hoặc có biện pháp pháp lý nếu bán hàng giả/nhái. | Điều khoản dịch vụ Shopee |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Làm sao để trả hàng... | RecursiveChunker | Có (Cả 3 thành viên đều có) | Dễ tìm vì từ khóa xuất hiện nhiều. Score cao nhất: ~0.71 |
| 2 | Thời gian hoàn tiền... | RecursiveChunker | Có (Chỉ TV2, TV3) | Cần ngữ cảnh dài để gom đủ thông tin số ngày. Score cao nhất: ~0.65 |
| 3 | Tiki thu thập... | SentenceChunker | Có | Câu trả lời nằm gọn trong 1 câu. Score cao nhất: ~0.68 |
| 4 | Hàng dễ vỡ... | RecursiveChunker | Có | Cần đoạn văn quy định đóng gói. Score cao nhất: ~0.62 |
| 5 | Bán hàng giả... | FixedSizeChunker | Có | Dễ bắt trùng từ khóa "hàng giả/nhái". Score cao nhất: ~0.66 |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Rất hữu ích ở câu hỏi 3 ("Tiki thu thập thông tin..."). Nếu không có metadata lọc theo `source_url` chứa chữ "tiki", hệ thống có thể bốc nhầm chính sách bảo mật của Shopee (vì có nhiều từ khóa trùng lặp như "thu thập thông tin khách hàng").

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - Việc sử dụng mô hình embedding thương mại (`text-embedding-3-small`) đem lại sự khác biệt hoàn toàn về độ chính xác so với mock.
> - Kích thước Chunk (Chunk Size) ảnh hưởng trực tiếp đến khả năng hiểu ngữ cảnh của LLM.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một tài liệu nhưng nếu cắt câu quá ngắn, LLM không đủ cơ sở để trả lời. Ngược lại cắt quá to lại dễ lẫn lộn thông tin. Chiến lược chia đệ quy với overlap khoảng 10-20% chiều dài là mức lý tưởng.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ gắn thêm nhiều trường metadata chi tiết hơn, ví dụ `topic` = "hoàn tiền", "giao hàng", "bảo mật" để hỗ trợ truy xuất, và loại bỏ các đoạn HTML/boilerplate thừa để nâng cao chất lượng văn bản.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
