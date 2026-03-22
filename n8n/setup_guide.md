# n8n Workflow 設定說明

## 前置確認

確認以下服務都在運行：
- n8n：http://127.0.0.1:5678
- Ollama：執行 `ollama list` 確認 minimax-m2:cloud 在列表中

---

## 步驟一：開啟 n8n 並匯入 Workflow

1. 瀏覽器開啟 **http://127.0.0.1:5678**
2. 登入 n8n（若有設定帳密的話）
3. 進入主畫面後，點選右上角的 **「+」** 或 **「New Workflow」**
4. 進入空白 Workflow 畫面後，點選右上角選單（三個點 `...`）
5. 選擇 **「Import from File」**（或 **「Import from JSON」**）
6. 選擇檔案：`C:\contract-review-system\n8n\workflow_template.json`
7. 確認匯入後，畫面應出現三個已連接的節點：
   ```
   [Webhook] → [HTTP Request] → [Code]
   ```

---

## 步驟二：確認各節點設定

### Webhook 節點
點擊 Webhook 節點，確認：
- HTTP Method：**POST**
- Path：**analyze**
- Response Mode：**Last Node**

> 匯入後 n8n 會自動產生完整的 Webhook URL，格式類似：
> `http://127.0.0.1:5678/webhook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
(http://localhost:5678/webhook/analyze)
> **請記錄這個 URL**，後面需要填入 backend/.env

### HTTP Request 節點
點擊 HTTP Request 節點，確認：
- Method：**POST**
- URL：`http://127.0.0.1:11434/api/generate`
(http://127.0.0.1:11434/api/generate)
- Body：Raw JSON（內含 minimax-m2:cloud 模型名稱）

### Code 節點
點擊 Code 節點，確認 JavaScript 代碼已載入（應有大量中文注釋）

---

## 步驟三：啟用 Workflow

1. 確認節點都設定正確後
2. 點擊右上角的 **「Inactive」** 切換開關，讓它變成 **「Active」**（綠色）
3. 此時 Webhook URL 正式生效，可以接收請求

---

## 步驟四：更新後端 Webhook URL

1. 確認 Webhook 節點顯示的完整 URL（例如 `http://127.0.0.1:5678/webhook/abc123...`）
2. 在後端設定：
   ```bash
   # 建立 backend/.env 檔案（如果不存在）
   echo N8N_WEBHOOK_URL=http://127.0.0.1:5678/webhook/你的實際URL > C:\contract-review-system\backend\.env
   ```
3. 重新啟動後端服務使設定生效

> **注意**：若 Workflow 使用「Test」模式，URL 格式是 `/webhook-test/...`；
> 啟用（Active）後才是 `/webhook/...`，請確認使用的是 Active 狀態的 URL

---

## 步驟五：測試 Workflow

### 方法一：n8n UI 測試
1. 點擊 Webhook 節點
2. 點擊「**Listen for Test Event**」
3. 另開終端機執行：
```bash
curl -X POST http://127.0.0.1:5678/webhook-test/analyze \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"第一條 退費條款：租客不得退款。第二條 責任限制：房東無責任。第三條 自動扣費：房東可自動扣費。\", \"filename\": \"test.pdf\"}"
```
4. 確認 n8n 畫面中三個節點都變成綠色（執行成功）

### 方法二：直接測試 Active Webhook
```bash
# 將 YOUR_WEBHOOK_ID 換成實際的 webhook ID
curl -X POST http://127.0.0.1:5678/webhook/YOUR_WEBHOOK_ID \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"第一條 退費條款：租客不得退款。第二條 責任限制：房東無責任。第三條 自動扣費：房東可自動扣費。\", \"filename\": \"test.pdf\"}"
```

---

## 預期回傳結果

正確執行後應收到類似以下的 JSON：

```json
{
  "violations": [
    {
      "id": 1,
      "clause": "不合理退費條款",
      "riskLevel": "高",
      "reason": "違反消保法第 19 條",
      "details": "消費者享有法定退費權利"
    },
    {
      "id": 2,
      "clause": "全面免責條款",
      "riskLevel": "高",
      "reason": "違反消保法第 7 條",
      "details": "不得以契約完全免除責任"
    },
    {
      "id": 3,
      "clause": "自動扣費／自動續約條款",
      "riskLevel": "高",
      "reason": "違反消保法第 17 條",
      "details": "自動扣費需事先取得消費者明確同意"
    }
  ],
  "riskScore": 9,
  "totalViolations": 3,
  "summary": "本合約共偵測到 3 個疑似違法條款，風險評分 9/10。建議簽署前諮詢專業人士。"
}
```

---

## 常見問題排除

| 問題 | 症狀 | 解決方法 |
|------|------|---------|
| Ollama 無回應 | HTTP Request 節點逾時 | 執行 `ollama serve` 確認服務啟動 |
| 模型找不到 | Ollama 回傳 model not found | 執行 `ollama pull minimax-m2:cloud` |
| Webhook 無法接收 | curl 回傳連線拒絕 | 確認 Workflow 已 Active（非 Inactive）|
| Code 節點錯誤 | 顯示 JavaScript 錯誤 | 重新從檔案匯入 workflow_template.json |
| 回傳空的 violations | violations 陣列為 [] | 確認 Ollama 有回傳內容，或檢查 text 欄位是否正確傳入 |
