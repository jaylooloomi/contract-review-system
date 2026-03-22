# Day 1 Claude Code 執行清單
# 台灣消費者合約自動審閱系統

**執行模式**：Claude Code 逐步執行，每個時段完成後強制等待使用者確認驗證通過，才繼續下一個時段。
**禁止行為**：不得假設驗證通過、不得自動跳段、發現錯誤必須停下報告。

---

## 執行規則（Claude Code 必須遵守）

1. 每個時段的「Claude 執行項目」由 Claude Code 直接完成（建立檔案、執行指令）
2. 執行完畢後，列出「驗證清單」讓使用者操作確認
3. 遇到 `⛔ 停止點` 必須停下，**等使用者明確回覆「通過」、「OK」或「繼續」後才能執行下一個時段**
4. 若任何驗證失敗，立即停止並回報問題，不得繼續

---

## 時段 1 — FastAPI 後端框架

**目標**：建立可運行的 FastAPI 後端，能接收 PDF 並呼叫 n8n webhook
**估計時間**：1 小時

### Claude 執行項目

- [ ] **1-1** 建立 `backend/` 目錄
- [ ] **1-2** 建立 `backend/requirements.txt`，內容：
  ```
  fastapi==0.111.0
  uvicorn[standard]==0.29.0
  pdfplumber==0.11.0
  httpx==0.27.0
  python-multipart==0.0.9
  pytest==8.2.0
  pytest-asyncio==0.23.7
  ```
- [ ] **1-3** 建立 `backend/main.py`，需包含：
  - FastAPI 應用程式初始化，CORS middleware 設定（允許 http://127.0.0.1:5173）
  - 詳細 logging 設定（INFO 等級，含時間戳記）
  - `GET /health` 端點，回傳 `{"status": "healthy", "service": "contract-review-backend", "timestamp": "<當前時間>"}`
  - `POST /api/analyze` 端點，接收 PDF 檔案（form-data, key="file"），用 pdfplumber 提取文字，呼叫 n8n webhook（`http://127.0.0.1:5678/webhook/analyze`），回傳分析結果
  - n8n webhook URL 用環境變數 `N8N_WEBHOOK_URL` 控制，預設值 `http://127.0.0.1:5678/webhook/analyze`
  - 回傳 JSON 格式：`{"success": true, "filename": "...", "originalText": "...", "analysisResult": {...}, "timestamp": "..."}`
- [ ] **1-4** 建立 `backend/test_api.py`，包含 30+ 個測試案例：
  - `/health` 端點測試（狀態碼、JSON 格式、必要欄位）
  - `/api/analyze` 端點測試（上傳 PDF、回傳格式、欄位驗證、錯誤處理）
  - 邊界情況（空檔案、非 PDF 格式、超大檔案）
- [ ] **1-5** 執行：`cd C:\contract-review-system\backend && pip install -r requirements.txt`
- [ ] **1-6** 執行：`python -m py_compile main.py`（確認無語法錯誤）
- [ ] **1-7** 在背景啟動服務：`uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

### 驗證步驟（使用者執行以下指令確認）

```bash
# 驗證 1：health 端點
curl http://127.0.0.1:8000/health

# 預期回傳：
# {"status":"healthy","service":"contract-review-backend","timestamp":"..."}

# 驗證 2：Swagger 文件
# 瀏覽器開啟：http://127.0.0.1:8000/docs
# 應看到 /health 和 /api/analyze 兩個端點

# 驗證 3：測試案例列表
cd C:\contract-review-system\backend
pytest test_api.py --collect-only
# 應列出 30+ 個測試案例，無語法錯誤
```

### ⛔ 停止點 1 — 等待使用者確認

**Claude Code 在此停下，不得繼續執行時段 2。**

請使用者確認以下項目全部通過後，回覆「時段1通過」：
- [ ] `curl /health` 回傳 200 狀態碼，JSON 格式正確
- [ ] 瀏覽器能開啟 `/docs`，看到兩個端點
- [ ] `pytest --collect-only` 能列出 30+ 個測試，無語法錯誤

---

## 時段 2 — n8n Workflow 配置

**目標**：在 n8n 中配置完整的分析工作流，使用 minimax-m2:cloud 模型
**估計時間**：1.75 小時
**注意**：n8n 為 UI 操作，Claude 負責產出設定檔和操作說明，使用者依指示在 n8n UI 中操作

### Claude 執行項目

- [ ] **2-1** 建立 `n8n/` 目錄
- [ ] **2-2** 建立 `n8n/code_node.js`，包含完整的 JavaScript 邏輯：
  - 從 HTTP Request 節點取得 Ollama 回應
  - 解析 JSON 回應（若回應含 Markdown code block 需去除）
  - 若解析失敗則使用關鍵詞匹配備援方案（退費、責任限制、自動扣費、自動續約等）
  - 計算風險評分 1-10（每個高風險條款 +3，中風險 +2，低風險 +1，上限 10）
  - 回傳 `{ violations: [...], riskScore: N, totalViolations: N, summary: "..." }`
  - 每個 violation 物件格式：`{ id: N, clause: "...", riskLevel: "高/中/低", reason: "...", details: "..." }`
- [ ] **2-3** 建立 `n8n/workflow_template.json`，這是可直接匯入 n8n 的完整 workflow JSON，包含：
  - Webhook 節點（HTTP Method: POST, Path: analyze）
  - HTTP Request 節點（URL: `http://127.0.0.1:11434/api/generate`, Method: POST, 呼叫 minimax-m2:cloud）
  - Code 節點（使用 2-2 的邏輯）
  - 三個節點正確連接
- [ ] **2-4** 建立 `n8n/setup_guide.md`，逐步 UI 操作說明，包含：
  - 如何在 n8n 匯入 workflow_template.json
  - 如何確認 Webhook URL
  - 如何手動執行測試
  - 提供完整的 curl 測試指令

### 驗證步驟（使用者操作）

```bash
# 步驟 1：開啟 n8n UI
# 瀏覽器：http://127.0.0.1:5678

# 步驟 2：匯入 workflow
# 點選右上角選單 → Import from File → 選擇 n8n/workflow_template.json

# 步驟 3：啟用 Workflow（點 Active 開關）

# 步驟 4：用 curl 測試（使用 n8n 顯示的實際 Webhook URL）
curl -X POST http://127.0.0.1:5678/webhook/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "第一條 退費條款：租客不得退款。第二條 責任限制：房東無責任。第三條 自動扣費：房東可自動扣費。", "filename": "test.pdf"}'

# 預期回傳包含：
# {"violations": [...], "riskScore": 7-10, "totalViolations": 3, "summary": "..."}
```

### ⛔ 停止點 2 — 等待使用者確認

**Claude Code 在此停下，不得繼續執行時段 3。**

請使用者確認以下項目全部通過後，回覆「時段2通過」：
- [ ] workflow 已成功匯入並啟用
- [ ] curl 測試回傳包含 violations 陣列
- [ ] riskScore 為 1-10 之間的數字
- [ ] totalViolations 與 violations 陣列長度相符
- [ ] 將 n8n 顯示的 Webhook URL 記錄下來（例如 `http://127.0.0.1:5678/webhook/xxxxxxxx`），並更新 `backend/.env` 中的 `N8N_WEBHOOK_URL`

---

## 時段 3 — Dify 知識庫配置

**目標**：在 Dify 建立台灣消保法知識庫
**估計時間**：1.25 小時
**注意**：Dify 為 UI 操作，Claude 負責準備知識庫文件和操作說明

### Claude 執行項目

- [ ] **3-1** 建立 `dify/` 目錄
- [ ] **3-2** 建立 `dify/taiwan_cpa_knowledge.md`，包含 20 條**真實**的台灣消費者保護法條文：
  - 必須使用真實的條號和條文內容
  - 每條格式：`## 第 X 條 — 條文標題\n核心內容（50-100字）\n違規後果或執法機關說明`
  - 涵蓋：定義條款（第2條）、責任限制（第7條）、廣告效力（第22條）、不公平契約（第12條）、標準契約審查（第17條）、特種買賣（第19條）等重要條款
- [ ] **3-3** 建立 `dify/setup_guide.md`，逐步 UI 操作說明：
  - 建立知識庫（名稱：taiwan_cpa，語言：中文）
  - 上傳 taiwan_cpa_knowledge.md
  - 設定 Embedding Model 為 nomic-embed-text
  - 設定 LLM 為 minimax-m2:cloud
  - 設定 Retrieval Mode 為 Hybrid，Top K=5，Similarity Threshold=0.5
  - 如何取得 Knowledge Base ID 和 API Key
- [ ] **3-4** 建立 `dify/test_queries.md`，包含 3 個測試查詢及預期回應：
  - 查詢 1：「自動扣費是否合法？」→ 預期回傳第 X 條相關內容
  - 查詢 2：「責任限制條款有什麼限制？」→ 預期回傳第 7 條相關內容
  - 查詢 3：「如何判斷不公平標準契約條款？」→ 預期回傳第 12 條相關內容

### 驗證步驟（使用者操作）

```
步驟 1：開啟 Dify UI
瀏覽器：http://127.0.0.1:3001

步驟 2：依照 dify/setup_guide.md 建立知識庫並上傳文件
等待 Embedding 進度條完成（100%）

步驟 3：在知識庫的「測試」介面執行以下查詢（參考 dify/test_queries.md）：
- 查詢 1：「自動扣費是否合法？」
- 查詢 2：「責任限制條款有什麼限制？」
- 查詢 3：「如何判斷不公平標準契約條款？」

每個查詢應回傳相關的法律條文（相關性評分 > 0.5）

步驟 4：記錄 Knowledge Base ID 和 API Key
（在知識庫設定頁面可以找到）
```

### ⛔ 停止點 3 — 等待使用者確認

**Claude Code 在此停下，不得繼續執行時段 5。**

請使用者確認以下項目全部通過後，回覆「時段3通過」並提供 Knowledge Base ID 和 API Key：
- [ ] Dify 知識庫建立成功
- [ ] taiwan_cpa_knowledge.md 已上傳，Embedding 100% 完成
- [ ] 3 個測試查詢都回傳相關法律條文（不是無關內容）
- [ ] Knowledge Base ID 已記錄
- [ ] API Key 已記錄

---

## 時段 4 — 午餐休息

**休息時間，Claude 不需要執行任何項目。**

---

## 時段 5 — 系統集成測試

**目標**：驗證完整流程：前端上傳 → 後端提取 → n8n 分析 → 回傳結果
**估計時間**：1 小時
**前提**：時段 1、2、3 都已確認通過

### Claude 執行項目

- [ ] **5-1** 確認所有服務狀態（依次執行以下確認）：
  - `curl http://127.0.0.1:8000/health` → 確認後端運行
  - `curl http://127.0.0.1:5678` → 確認 n8n 運行（或瀏覽器訪問）
  - `ollama list` → 確認 minimax-m2:cloud 在列表中
- [ ] **5-2** 建立 `test/` 目錄，用 Python 建立測試 PDF `test/test_contract.pdf`：
  ```python
  # 使用 reportlab 或 fpdf2 建立包含以下內容的 PDF：
  # 甲乙雙方合約
  # 第一條 退費政策：消費者一旦付款，概不退費，不論任何原因。
  # 第二條 責任限制：本公司對因使用本服務造成的任何損失概不負責，包括間接損失。
  # 第三條 自動續約：本合約到期後自動續約一年，並自動扣取費用，不另行通知。
  # 第四條 爭議處理：所有爭議由本公司單方面決定，消費者不得提出異議。
  ```
- [ ] **5-3** 執行完整 API 流程測試：
  ```bash
  cd C:\contract-review-system
  curl -X POST http://127.0.0.1:8000/api/analyze \
    -F "file=@test/test_contract.pdf"
  ```
- [ ] **5-4** 執行 pytest 測試：
  ```bash
  cd C:\contract-review-system\backend
  pytest test_api.py -v 2>&1 | tee ../test/pytest_results.txt
  ```
- [ ] **5-5** 將測試結果完整輸出給使用者查看

### 驗證步驟（使用者確認）

```
驗證 1：curl 測試結果必須包含以下 JSON 結構：
{
  "success": true,
  "filename": "test_contract.pdf",
  "originalText": "...",  ← 不為空
  "analysisResult": {
    "violations": [...],  ← 陣列，至少有 2 個 violation
    "riskScore": ...,     ← 1-10 之間的整數
    "totalViolations": N, ← 等於 violations 長度
    "summary": "..."      ← 不為空字串
  },
  "timestamp": "..."
}

驗證 2：每個 violation 物件必須包含：
{ "id": N, "clause": "...", "riskLevel": "高/中/低", "reason": "...", "details": "..." }

驗證 3：pytest 結果
顯示每個測試的 PASS/FAIL 狀態
（允許部份 FAIL，但需記錄哪些失敗及原因）
```

### ⛔ 停止點 5 — 等待使用者確認

**Claude Code 在此停下，不得繼續執行時段 6。**

請使用者確認以下項目後，回覆「時段5通過」：
- [ ] curl 測試回傳 200 狀態碼
- [ ] JSON 結構完整（success, filename, originalText, analysisResult, timestamp）
- [ ] violations 陣列至少有 1 個項目
- [ ] riskScore 在 1-10 之間
- [ ] pytest 執行完畢（記錄通過/失敗數量）

---

## 時段 6 — Vue 3 前端開發

**目標**：開發 Vue 3 前端，展示上傳頁面和分析結果
**估計時間**：1.75 小時

### Claude 執行項目

- [ ] **6-1** 建立 Vue 3 + Vite 專案：
  ```bash
  cd C:\contract-review-system
  npm create vite@latest frontend -- --template vue
  ```
- [ ] **6-2** 安裝依賴：
  ```bash
  cd C:\contract-review-system\frontend
  npm install
  npm install vue-router@4 axios tailwindcss postcss autoprefixer
  ```
- [ ] **6-3** 初始化 Tailwind CSS：
  ```bash
  npx tailwindcss init -p
  ```
- [ ] **6-4** 建立 `frontend/tailwind.config.js`：
  ```js
  export default {
    content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
    theme: { extend: {} },
    plugins: [],
  }
  ```
- [ ] **6-5** 在 `frontend/src/style.css` 頂部加入 Tailwind directives：
  ```css
  @tailwind base;
  @tailwind components;
  @tailwind utilities;
  ```
- [ ] **6-6** 建立 `frontend/src/router/index.js`，設定兩個路由：
  - `/` → `UploadPage`（上傳頁面）
  - `/annotation` → `AnnotationPage`（結果展示頁面）
- [ ] **6-7** 建立 `frontend/src/views/UploadPage.vue`，功能：
  - 標題「台灣消費者合約審閱系統」
  - 拖放區域 / 點擊選擇 PDF 檔案
  - 顯示已選擇的檔名
  - 「開始分析」按鈕
  - 上傳中的 Loading 動畫
  - 呼叫 `POST http://127.0.0.1:8000/api/analyze`（axios multipart/form-data）
  - 成功後將回傳資料存入 localStorage，導航到 `/annotation`
  - 失敗時顯示錯誤訊息
- [ ] **6-8** 建立 `frontend/src/views/AnnotationPage.vue`，功能：
  - 從 localStorage 讀取分析資料
  - 頂部顯示風險評分（1-10），用顏色區分等級（紅/橙/綠）
  - 總結文字（summary）
  - 違法條款列表（每個 violation 顯示：條款名稱、風險等級、原因、詳細說明）
  - 原文區域，高亮顯示違法詞語（用 `<mark>` 標籤）
  - 「返回上傳」按鈕（導航回 `/`）
- [ ] **6-9** 更新 `frontend/src/App.vue` 加入 `<RouterView />`
- [ ] **6-10** 更新 `frontend/src/main.js` 掛載 router
- [ ] **6-11** 啟動開發伺服器：
  ```bash
  cd C:\contract-review-system\frontend
  npm run dev
  ```

### 驗證步驟（使用者完整流程測試）

```
步驟 1：開啟前端
瀏覽器：http://127.0.0.1:5173

步驟 2：上傳頁面
確認看到標題和上傳區域

步驟 3：選擇 test/test_contract.pdf 上傳
確認顯示 Loading 動畫

步驟 4：等待分析完成
確認自動導航到 /annotation 結果頁面

步驟 5：結果頁面
- 確認顯示風險評分（有顏色區分）
- 確認顯示違法條款列表
- 確認原文有高亮標記
- 確認「返回上傳」按鈕可用

步驟 6：瀏覽器開發者工具 Console
確認沒有 error 級別的錯誤（warning 可以接受）
```

### ⛔ 停止點 6 — 等待使用者確認

**Claude Code 在此停下，不得繼續執行時段 7。**

請使用者確認以下項目後，回覆「時段6通過」：
- [ ] 前端能成功啟動（http://127.0.0.1:5173 可訪問）
- [ ] 上傳頁面正常顯示
- [ ] 能選擇並上傳 PDF
- [ ] 成功導航到結果頁面
- [ ] 結果頁面正確顯示風險評分和違法條款
- [ ] 原文高亮功能正常
- [ ] 無致命 Console 錯誤

---

## 時段 7 — 最終測試與驗收

**目標**：驗證整個系統端對端工作正常
**估計時間**：0.5 小時

### Claude 執行項目

- [ ] **7-1** 提供完整的端對端驗收清單（對應 Day1_RealExecution_Plan.md 所有完成標誌）
- [ ] **7-2** 記錄開發過程中遇到的任何問題和解決方案（建立 `docs/known_issues.md`）

### 最終驗收清單

請使用者逐一確認以下所有項目：

**時段 1 — 後端**
- [ ] FastAPI 服務運行中（http://127.0.0.1:8000）
- [ ] `/health` 端點正常
- [ ] `/docs` Swagger 可訪問
- [ ] requirements.txt 所有套件安裝完成

**時段 2 — n8n**
- [ ] n8n workflow 已匯入並啟用
- [ ] Webhook 能接收 POST 請求
- [ ] Ollama minimax-m2:cloud 呼叫成功
- [ ] Code Node 回傳正確 JSON 格式

**時段 3 — Dify**
- [ ] 知識庫 taiwan_cpa 已建立
- [ ] 20 條消保法條款已上傳，Embedding 完成
- [ ] 3 個測試查詢回傳準確法條

**時段 5 — 集成測試**
- [ ] 完整 API 流程（上傳 PDF → 回傳分析結果）正常
- [ ] JSON 結構符合規格
- [ ] pytest 測試執行完畢

**時段 6 — 前端**
- [ ] Vue 3 前端正常運行（http://127.0.0.1:5173）
- [ ] 完整流程（上傳→分析→結果顯示）正常
- [ ] 結果頁面顯示正確

**整體驗收標準**：
- 準確度 60% 以上（A 版本期望值，允許部份漏判但不得有大量誤判）
- 無致命 Bug，系統可使用

### ⛔ 停止點 7 — Day 1 完成確認

**等使用者確認全部驗收清單後，回覆「Day1完成」。**

---

## 目錄結構（執行完成後）

```
C:\contract-review-system\
├── Day1_RealExecution_Plan.md    ← 原始計畫
├── Day1_claude_todolist.md       ← 本文件
├── backend\
│   ├── main.py                   ← FastAPI 應用
│   ├── requirements.txt          ← Python 依賴
│   └── test_api.py               ← pytest 測試
├── n8n\
│   ├── workflow_template.json    ← 可匯入的 workflow
│   ├── code_node.js              ← Code Node 邏輯
│   └── setup_guide.md            ← n8n UI 操作說明
├── dify\
│   ├── taiwan_cpa_knowledge.md   ← 20 條消保法條文
│   ├── setup_guide.md            ← Dify UI 操作說明
│   └── test_queries.md           ← 測試查詢與預期回應
├── frontend\
│   ├── src\
│   │   ├── views\
│   │   │   ├── UploadPage.vue    ← 上傳頁面
│   │   │   └── AnnotationPage.vue ← 結果展示頁面
│   │   ├── router\
│   │   │   └── index.js          ← 路由設定
│   │   ├── App.vue
│   │   └── main.js
│   ├── tailwind.config.js
│   └── package.json
└── test\
    ├── test_contract.pdf          ← 測試用合約 PDF
    └── pytest_results.txt         ← pytest 輸出記錄
```

---

## 現在開始執行時段 1

**Claude Code 請立即開始執行時段 1 的所有項目（1-1 到 1-7）。**
