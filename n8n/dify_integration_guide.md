# Dify 知識庫串接 n8n 操作說明

## 流程說明

串接後的完整流程：
```
PDF → FastAPI → n8n Webhook → Dify Retrieval → Ollama → Code Node → 回傳 JSON
```

Dify 的角色：接收合約文字，從知識庫撈出最相關的消保法條（top 3），
讓 Ollama 在分析時有具體法條依據，減少幻覺。

---

## 步驟一：取得 Dify API Key

1. 開啟 http://127.0.0.1:3001
2. 左側選單 → **設定（Settings）** → **API 金鑰（API Keys）**
3. 點「建立新金鑰」，複製 `sk-...` 開頭的金鑰
4. 記下來，後面會用到

---

## 步驟二：取得知識庫 Dataset ID

1. 左側選單 → **知識庫（Knowledge）**
2. 點進台灣消保法的知識庫
3. 看瀏覽器網址列，格式為：
   ```
   http://127.0.0.1:3001/datasets/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/documents
   ```
4. 複製中間那段 UUID（就是 Dataset ID）

---

## 步驟三：驗證 Dify Retrieval API 可用

用 curl 測試（把 KEY 和 ID 換成你的）：

```bash
curl -X POST http://127.0.0.1:3001/v1/datasets/DATASET_ID/retrieve \
  -H "Authorization: Bearer DIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"不得退款\", \"retrieval_model\": {\"search_method\": \"semantic_similarity\", \"top_k\": 3, \"score_threshold_enabled\": false}}"
```

預期回傳格式：
```json
{
  "records": [
    {
      "segment": {
        "content": "第十九條...",
        "document": { "name": "taiwan_cpa_knowledge.md" }
      },
      "score": 0.87
    }
  ]
}
```

---

## 步驟四：在 n8n 更新 workflow

### 方式 A：匯入新版 JSON（推薦）

1. 開啟 n8n → http://127.0.0.1:5678
2. 進入 Contract Analysis workflow
3. 右上角 **⋮** → **Import from file**
4. 選擇 `n8n/workflow_template.json`
5. 匯入後會出現 4 個 nodes：Webhook → Dify Retrieval → HTTP Request → Code

### 方式 B：手動新增 node

1. 在 Webhook 和 HTTP Request 之間插入新的 **HTTP Request** node
2. 命名為 `Dify Retrieval`
3. 設定如下：
   - Method: `POST`
   - URL: `http://127.0.0.1:3001/v1/datasets/你的DATASET_ID/retrieve`
   - Headers:
     - `Authorization`: `Bearer 你的API_KEY`
     - `Content-Type`: `application/json`
   - Body (Raw JSON):
     ```json
     {"query": "{{ $node['Webhook'].json.body?.text || $node['Webhook'].json.text }}", "retrieval_model": {"search_method": "semantic_similarity", "top_k": 3, "score_threshold_enabled": false}}
     ```
4. 把 Webhook → Dify Retrieval → HTTP Request 的連線接好

---

## 步驟五：更新 Ollama HTTP Request node

把原本 Ollama 的 Body 改為新版（已包含法條注入）：

```
你是台灣消費者保護法專家。請分析以下合約文本，找出所有違反台灣消費者保護法的條款。

【相關法條參考（來自知識庫）】
{{ ($node['Dify Retrieval'].json.records || []).map(r => r.segment && r.segment.content ? r.segment.content : '').filter(s => s).join('\n---\n') || '（知識庫查詢無結果）' }}

請以JSON格式回傳...（其餘 prompt 不變）

【合約文本】
{{ $node['Webhook'].json.body?.text || $node['Webhook'].json.text }}
```

---

## 步驟六：更新 Code Node 為 v2

把 Code Node 的內容換成 `n8n/code_node_v2.js` 的完整內容。

---

## 步驟七：測試

```bash
curl -s -X POST http://127.0.0.1:8000/api/analyze \
  -F "file=@C:\contract-review-system\test\test_contract.pdf"
```

確認回傳的 `violations[].reason` 中有引用具體法條（如「違反消保法第19條」），
代表 Dify 法條有成功注入。

---

## 常見問題

**Q: Dify Retrieval 回傳 401**
→ API Key 錯誤，重新從 Dify 設定頁複製

**Q: Dify Retrieval 回傳 404**
→ Dataset ID 錯誤，重新從知識庫網址列複製 UUID

**Q: records 是空陣列**
→ 知識庫文件未索引完成，到 Dify 知識庫頁確認狀態為「可用」

**Q: Dify 回傳 502**
→ 重啟 nginx：`docker compose restart nginx`（參考 dify/setup_guide.md）
