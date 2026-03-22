# Dify 知識庫設定說明

## 前置確認
- Dify 服務：http://127.0.0.1:3001 可訪問
- Ollama 已安裝 nomic-embed-text：執行 `ollama list` 確認

若 nomic-embed-text 尚未安裝：
```bash
ollama pull nomic-embed-text
```

---

## 步驟一：登入 Dify

1. 瀏覽器開啟 **http://127.0.0.1:3001**
2. 登入帳號

---

## 步驟二：建立知識庫

1. 左側選單點選 **「Knowledge」**（知識庫）
2. 點選右上角 **「Create Knowledge」**
3. 填入：
   - Name（名稱）：`taiwan_cpa`
   - Description：`台灣消費者保護法重要條文知識庫`
4. 點選 **「Create」** 建立

> 建立後記下畫面中的 **Knowledge Base ID**（URL 中可看到，格式如 `/knowledge/xxxxxxxx-xxxx-xxxx-xxxx`）

---

## 步驟三：上傳知識庫文件

1. 進入剛建立的 `taiwan_cpa` 知識庫
2. 點選 **「Add File」** 或 **「Upload」**
3. 選擇檔案：`C:\contract-review-system\dify\taiwan_cpa_knowledge.md`
4. 上傳設定：
   - Indexing Method：**High Quality**（高品質，使用 Embedding）
   - Embedding Model：選擇 **nomic-embed-text**（需透過 Ollama）
   - Retrieval Mode：**Hybrid Search**（混合搜尋）
5. 點選 **「Save & Process」**
6. 等待 Embedding 進度條跑到 **100%**（可能需要 1-3 分鐘）

---

## 步驟四：確認 Embedding 完成

1. 進度條顯示 **完成** 或狀態變為 **Available**
2. 文件列表中可看到 `taiwan_cpa_knowledge.md`，狀態為已索引
3. 確認 Chunk 數量大於 0（應該有 15-20 個 chunks）

---

## 步驟五：取得 API Key

1. 點選左側選單 **「Settings」**（設定）或 **「API」**
2. 找到 **API Key** 區塊
3. 點選 **「Create New Secret Key」**
4. 複製並記錄 API Key（格式：`app-xxxxxxxxxxxxxxxxxxxxxxxx`）

---

## 步驟六：測試知識庫

1. 回到 `taiwan_cpa` 知識庫
2. 點選右上角 **「Test」** 或 **「Retrieval Testing」**
3. 依序輸入以下測試查詢（參考 test_queries.md 的預期結果）：

**測試查詢 1**：
```
自動扣費是否合法？
```

**測試查詢 2**：
```
責任限制條款有什麼限制？
```

**測試查詢 3**：
```
如何判斷不公平標準契約條款？
```

每個查詢應回傳相關的法律條文段落（相關性分數建議 > 0.5）

---

## 步驟七：記錄關鍵資訊

請記錄以下資訊，時段 5 集成測試時需要：

| 項目 | 值 |
|------|-----|
| Knowledge Base ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| API Key | `app-xxxxxxxxxxxxxxxxxxxxxxxx` |
| Embedding Model | `nomic-embed-text` |
| Dify URL | `http://127.0.0.1:3001` |

---

## 常見問題

| 問題 | 原因 | 解決方法 |
|------|------|---------|
| Embedding 失敗 | nomic-embed-text 未下載 | `ollama pull nomic-embed-text` |
| 上傳後狀態卡住 | Ollama 服務未運行 | 確認 `ollama serve` 已執行 |
| 查詢回傳空結果 | Embedding 未完成 | 等進度條到 100% 再測試 |
| 查詢結果不相關 | chunk 設定問題 | 嘗試調低 Similarity Threshold 至 0.3 |
| 重啟後 502 Bad Gateway | nginx 快取舊 API 容器 IP | `cd C:\dify\dify\docker && docker compose restart nginx` |
