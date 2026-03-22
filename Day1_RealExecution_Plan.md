# Day 1 階段 A 執行計畫 - 真實驗證版本

**項目名稱**：台灣消費者合約自動審閱系統  
**執行日期**：2024-01-01  
**執行模式**：真實執行 + 共同驗證（拒絕假資料）  
**模型**：minimax-m2:cloud（通過 Ollama）  
**策略**：每段完成後通知你驗證，確保錯誤就是錯誤

---

## 📋 執行原則

### 🚫 禁止項目
- ❌ 不寫假代碼
- ❌ 不寫假測試結果
- ❌ 不寫假 API 響應
- ❌ 不跳過任何驗證步驟
- ❌ 發現錯誤不隱瞞

### ✅ 必需項目
- ✅ 每段代碼都能實際運行
- ✅ 每段完成後立即通知你
- ✅ 提供具體的驗證方法
- ✅ 等待你驗證後再進行下一段
- ✅ 錯誤時立即停止並報告

---

## 時間分配

| 時段 | 任務 | 估計時間 | 驗證方式 |
|------|------|--------|--------|
| 1 | 後端框架 | 1 小時 | 手動執行 FastAPI，檢查是否啟動 |
| 2 | n8n Workflow | 1.75 小時 | 在 n8n UI 中手動測試，驗證返回結果 |
| 3 | Dify 知識庫 | 1.25 小時 | 在 Dify UI 中手動測試，驗證查詢結果 |
| 4 | 午餐休息 | 1 小時 | - |
| 5 | 系統集成測試 | 1 小時 | 用 curl 或 Postman 完整測試流程 |
| 6 | 前端開發 | 1.75 小時 | 瀏覽器訪問，手動上傳和查看結果 |
| 7 | 最終測試 | 0.5 小時 | 完整端到端測試 |
| **總計** | | **9 小時** | **全部手動驗證** |

---

## 時段 1：後端框架（9:00-10:00 AM）

### 目標
創建可運行的 FastAPI 後端，能接收 PDF 並調用 n8n webhook

### 執行步驟

#### Step 1：更新 main.py
**動作**：將後端代碼更新為使用 minimax-m2:cloud 模型
- 添加詳細日誌（用於排查問題）
- 配置 n8n webhook URL
- 支援 PDF 提取（pdfplumber 優先）

**完成標誌**：
- [ ] main.py 檔案已更新
- [ ] 代碼能無語法錯誤通過 python -m py_compile main.py

#### Step 2：安裝依賴
**動作**：安裝 requirements.txt 中的所有包
```
執行：pip install -r requirements.txt
```

**完成標誌**：
- [ ] 所有包安裝成功
- [ ] 沒有依賴版本衝突

#### Step 3：啟動後端服務
**動作**：啟動 FastAPI 開發服務器
```
執行：cd C:\contract-review-system\backend
python main.py
```

**完成標誌**：
- [ ] 控制台顯示「Uvicorn running on http://0.0.0.0:8000」
- [ ] 沒有啟動錯誤

#### Step 4：驗證 /health 端點
**動作**：測試服務是否正常運行
```
執行：curl http://127.0.0.1:8000/health
或在瀏覽器訪問：http://127.0.0.1:8000/health
```

**預期結果**：
```json
{
  "status": "healthy",
  "service": "contract-review-backend",
  "timestamp": "2024-01-01T10:00:00.000000"
}
```

**完成標誌**：
- [ ] 返回 200 狀態碼
- [ ] JSON 結構正確
- [ ] 服務確認運行中

#### Step 5：更新 test_api.py
**動作**：確保測試框架能運行
```
執行：pytest test_api.py --collect-only
```

**完成標誌**：
- [ ] 能列出所有 30+ 個測試用例
- [ ] 沒有語法錯誤

#### Step 6：驗證 API 端點存在
**動作**：檢查 Swagger 文檔
```
訪問：http://127.0.0.1:8000/docs
```

**完成標誌**：
- [ ] 能看到 /health 端點
- [ ] 能看到 /api/analyze 端點
- [ ] 兩個端點都有說明

### 時段 1 的產出物

| 檔案 | 狀態 | 驗證方法 |
|------|------|--------|
| main.py | ✅ 更新中 | 運行後檢查日誌 |
| test_api.py | ✅ 驗證中 | pytest --collect-only |
| requirements.txt | ✅ 使用中 | pip install 檢查 |

### 🚨 時段 1 完成的標誌

**必須全部打勾才能進入時段 2：**
- [ ] main.py 無語法錯誤
- [ ] requirements.txt 所有包安裝成功
- [ ] FastAPI 能啟動
- [ ] /health 端點返回正確結果
- [ ] /docs 能訪問
- [ ] pytest 能列出所有測試

### ❌ 常見問題及對應

| 問題 | 症狀 | 對應 |
|------|------|------|
| 模塊導入失敗 | `ModuleNotFoundError` | 檢查 requirements.txt 是否完整安裝 |
| 端口被佔用 | `Address already in use` | 殺死佔用 8000 端口的進程 |
| PDF 提取失敗 | 返回 empty text | 檢查是否安裝 pdfplumber |
| CORS 錯誤 | 瀏覽器報 CORS 錯誤 | 確認 CORS middleware 配置 |

---

## 時段 2：n8n Workflow 配置（10:00-11:45 AM）

### 目標
在 n8n 中配置完整的分析工作流，使用 minimax-m2:cloud 模型

### 執行步驟

#### Step 1：打開 n8n UI
**動作**：訪問 n8n Web 界面
```
訪問：http://127.0.0.1:5678
```

**完成標誌**：
- [ ] n8n 登錄界面加載成功
- [ ] 能進入 Dashboard

#### Step 2：創建新 Workflow
**動作**：在 n8n 中創建新的工作流
- 點擊「Create Workflow」
- 命名為「Contract Analysis」

**完成標誌**：
- [ ] Workflow 創建成功
- [ ] 進入編輯界面

#### Step 3：添加 Webhook 節點
**動作**：添加 Webhook 觸發節點
- 點擊「+」添加節點
- 搜索「Webhook」
- 選擇第一個 Webhook 節點

**配置項**：
- HTTP Method：POST
- Path：/webhook/analyze

**完成標誌**：
- [ ] Webhook 節點已添加
- [ ] 顯示自動生成的 Webhook URL
- [ ] URL 格式：http://127.0.0.1:5678/webhook/xxxx

**重要**：複製這個 Webhook URL，待會要用到

#### Step 4：添加 HTTP Request 節點
**動作**：添加 HTTP 請求節點，調用 Ollama
- 點擊「+」添加節點
- 搜索「HTTP Request」
- 選擇 HTTP Request 節點

**配置項**：
- HTTP Method：POST
- URL：http://127.0.0.1:11434/api/generate
- Authentication：None

**Request Headers**：
- Content-Type：application/json

**Request Body**（Raw JSON）：
```json
{
  "model": "minimax-m2:cloud",
  "prompt": "檢測以下合約文本中的違法條款。請分析每個違法條款並返回JSON格式的結果。合約文本：{{$node['Webhook'].json.text}}",
  "stream": false
}
```

**完成標誌**：
- [ ] HTTP Request 節點已添加
- [ ] URL 正確指向 Ollama
- [ ] 模型名稱為 minimax-m2:cloud

#### Step 5：添加 Code Node
**動作**：添加代碼節點用於解析 Ollama 返回結果
- 點擊「+」添加節點
- 搜索「Code」
- 選擇 Code 節點

**代碼邏輯**：
需要編寫 JavaScript 代碼來：
1. 獲取 Ollama 的返回結果
2. 解析結果並提取違法條款
3. 計算風險評分（1-10）
4. 返回結構化的 JSON

**代碼框架**：
```javascript
// 1. 獲取上游節點的數據
const ollamaResult = $node["HTTP Request"].json;

// 2. 初始化結果數組
const violations = [];

// 3. 簡單的關鍵詞匹配（A 版本）
const keywords = {
  "退費": { name: "退費條款", level: "高" },
  "責任限制": { name: "責任限制", level: "中" },
  "自動扣費": { name: "自動扣費", level: "高" }
};

// 4. 檢測違法條款
// ... 添加檢測邏輯 ...

// 5. 計算風險評分
// ... 計算邏輯 ...

// 6. 返回結果
return {
  violations: violations,
  riskScore: riskScore,
  totalViolations: violations.length,
  summary: "..."
};
```

**完成標誌**：
- [ ] Code 節點已添加
- [ ] 代碼無語法錯誤
- [ ] 能正確訪問上游節點數據

#### Step 6：連接節點
**動作**：按照流程連接各個節點
```
Webhook → HTTP Request → Code Node
```

**完成標誌**：
- [ ] 三個節點都已連接
- [ ] 連接線清晰可見

#### Step 7：測試 Workflow
**動作**：手動測試整個工作流
- 點擊「Execute Workflow」按鈕
- 在 Webhook 節點中手動提供輸入數據

**測試數據**：
```json
{
  "text": "第一條 退費條款：租客不得退款。第二條 責任限制：房東無責任。第三條 自動扣費：房東可自動扣費。",
  "filename": "test.pdf"
}
```

**預期結果**（必須真實）：
- [ ] Webhook 節點接收數據
- [ ] HTTP Request 節點調用 Ollama 成功
- [ ] Code Node 解析結果並返回 JSON
- [ ] 返回的 JSON 包含：violations、riskScore、totalViolations、summary

**如果出現錯誤**：
- 檢查 Ollama 是否運行（ollama serve）
- 檢查 minimax-m2:cloud 是否已下載（ollama pull minimax-m2:cloud）
- 檢查 HTTP Request URL 是否正確
- 查看 n8n 的日誌了解具體錯誤

#### Step 8：導出 Workflow
**動作**：將配置導出以便備份
- 點擊菜單中的「Download」
- 保存為 workflow_export.json

**完成標誌**：
- [ ] workflow_export.json 文件已保存
- [ ] 文件大小 > 0

### 時段 2 的產出物

| 項目 | 必須驗證 |
|------|--------|
| Webhook URL | 複製並記錄 |
| HTTP Request 配置 | 測試調用 Ollama 成功 |
| Code Node 代碼 | 執行後返回正確 JSON |
| 完整流程 | 從 Webhook 到最終返回結果 |

### 🚨 時段 2 完成的標誌

**必須全部驗證成功才能進入時段 3：**
- [ ] Webhook URL 能正常接收 POST 請求
- [ ] HTTP Request 能調用 Ollama minimax-m2:cloud
- [ ] Code Node 能正確解析結果
- [ ] 完整工作流執行成功，返回正確的 JSON
- [ ] workflow_export.json 已保存

### ❌ 常見問題及對應

| 問題 | 症狀 | 對應 |
|------|------|------|
| Ollama 未運行 | HTTP Request 超時 | 執行 ollama serve |
| 模型未下載 | Ollama 返回模型未找到 | ollama pull minimax-m2:cloud |
| 節點連接錯誤 | 執行時顯示缺少輸入 | 檢查節點間的連線 |
| 代碼語法錯誤 | Code Node 執行失敗 | 檢查 JavaScript 語法 |

---

## 時段 3：Dify 知識庫配置（11:45 AM-1:00 PM）

### 目標
在 Dify 中建立台灣消保法知識庫，為 B 版本提高準確度

### 執行步驟

#### Step 1：打開 Dify UI
**動作**：訪問 Dify Web 界面
```
訪問：http://127.0.0.1:3001
```

**完成標誌**：
- [ ] Dify 登錄界面加載成功
- [ ] 能進入 Dashboard

#### Step 2：創建知識庫
**動作**：在 Dify 中創建新的知識庫
- 點擊「Knowledge Base」→「Create Knowledge」
- 輸入名稱：taiwan_cpa
- 選擇語言：中文

**完成標誌**：
- [ ] 知識庫創建成功
- [ ] 顯示知識庫 ID

**重要**：記錄下知識庫 ID，待會會用到

#### Step 3：準備知識庫文檔
**動作**：準備台灣消保法簡化版文檔
- 需要：20 個重點條款
- 格式：每個條款 50-100 字
- 包含：條款號、標題、核心內容

**重點條款清單**（必須真實的法律條款，不能胡編）：
1. 第 2 條 - 定義（消費者、企業經營者等定義）
2. 第 7 條 - 責任限制禁止（禁止無限制責任限制）
3. 第 10 條 - 爭議解決（申訴處理機制）
4. 第 12 條 - 不公平標準契約條款（判斷標準）
5. 第 17 條 - 禁止自動更新（需要明示同意）
6. 第 18 條 - 自動扣費禁止（禁止未經授權扣費）
7. ... （其他 13 個真實條款）

**完成標誌**：
- [ ] 文檔已準備
- [ ] 包含 20 個真實的消保法條款
- [ ] 格式統一（條款號、標題、內容）

#### Step 4：上傳知識庫文檔
**動作**：將文檔上傳到 Dify
- 在知識庫中點擊「Upload」
- 選擇準備好的文檔
- 等待 embedding 完成

**完成標誌**：
- [ ] 文檔已上傳
- [ ] Embedding 進度條完成（100%）
- [ ] 顯示「Upload successful」

#### Step 5：配置檢索參數
**動作**：配置知識庫的檢索方式
- Embedding Model：nomic-embed-text
- LLM：minimax-m2:cloud（需要通過 Ollama）
- Retrieval Mode：Hybrid
- Top K：5
- Similarity Threshold：0.5

**完成標誌**：
- [ ] 參數配置完成
- [ ] 所有設置都已保存

#### Step 6：測試知識庫
**動作**：手動測試知識庫查詢
- 在測試界面輸入查詢句子
- 檢查是否能返回相關條款

**測試查詢示例**（必須真實測試）：
1. "什麼是自動扣費禁止？" → 應該返回第 18 條相關內容
2. "責任限制的規則是什麼？" → 應該返回第 7 條相關內容
3. "怎樣判斷不公平標準契約條款？" → 應該返回第 12 條相關內容

**預期結果**：
- [ ] 能返回相關法律條款
- [ ] 相關性評分 > 0.5
- [ ] 返回結果準確（不能是亂七八糟的內容）

**如果出現問題**：
- 檢查 nomic-embed-text 是否已下載
- 檢查 minimax-m2:cloud 模型是否可用
- 檢查文檔是否正確上傳

#### Step 7：記錄配置信息
**動作**：保存 Dify 的關鍵信息
- Knowledge Base ID
- API Key
- Embedding Model 名稱
- LLM 模型名稱

**完成標誌**：
- [ ] 所有信息已記錄
- [ ] 信息能正確訪問 Dify API

### 時段 3 的產出物

| 項目 | 必須驗證 |
|------|--------|
| 知識庫創建 | 存在並可訪問 |
| 文檔上傳 | 20 個條款已上傳 |
| Embedding 完成 | 進度 100% |
| 測試查詢 | 3 個查詢都返回準確結果 |
| 配置信息 | Knowledge Base ID、API Key 已記錄 |

### 🚨 時段 3 完成的標誌

**必須全部驗證成功才能進入時段 5：**
- [ ] Dify 知識庫已創建
- [ ] 20 個真實的消保法條款已上傳
- [ ] Embedding 完成
- [ ] 手動測試的 3 個查詢都返回準確結果
- [ ] Knowledge Base ID 和 API Key 已記錄

### ❌ 常見問題及對應

| 問題 | 症狀 | 對應 |
|------|------|------|
| Embedding 失敗 | 進度條卡住 | 檢查 nomic-embed-text 是否下載 |
| 查詢結果不准 | 返回無關內容 | 檢查文檔內容是否正確 |
| API 調用失敗 | 503 錯誤 | 檢查 Dify 服務是否運行 |
| 模型不可用 | 返回模型錯誤 | 確認 minimax-m2:cloud 已下載 |

---

## 時段 4：午餐休息（1:00-2:00 PM）

充電時間 🍽️

---

## 時段 5：系統集成測試（2:00-3:00 PM）

### 目標
驗證完整的分析流程：前端上傳 → 後端提取 → n8n 分析 → 返回結果

### 執行步驟

#### Step 1：確認所有服務正常運行
**動作**：檢查三個核心服務狀態

**檢查清單**：
- [ ] FastAPI 後端：http://127.0.0.1:8000/health 返回 200
- [ ] n8n：http://127.0.0.1:5678 可訪問
- [ ] Ollama：ollama list 能列出 minimax-m2:cloud
- [ ] Dify：http://127.0.0.1:3001 可訪問

#### Step 2：準備測試 PDF
**動作**：準備一個真實的 PDF 檔案用於測試
- 建議內容：包含 2-3 個明顯的違法條款
- 格式：真實的 PDF（不能是文本假裝成 PDF）

**完成標誌**：
- [ ] 測試 PDF 已準備
- [ ] 檔案大小合理（> 1KB）

#### Step 3：手動上傳測試
**動作**：通過 API 端點上傳 PDF
```
工具：curl、Postman 或 Python 腳本
端點：POST http://127.0.0.1:8000/api/analyze
參數：form-data，key="file"，value=PDF 檔案
```

**完成標誌**：
- [ ] API 返回 200 狀態碼
- [ ] 返回的 JSON 包含以下字段：
  - success
  - filename
  - originalText
  - analysisResult
  - timestamp

#### Step 4：驗證返回結果格式
**動作**：檢查返回的 JSON 是否符合規格
```
應該包含：
{
  "success": true,
  "filename": "...",
  "originalText": "...",
  "analysisResult": {
    "violations": [...],
    "riskScore": 1-10,
    "totalViolations": N,
    "summary": "..."
  },
  "timestamp": "..."
}
```

**完成標誌**：
- [ ] success = true
- [ ] filename 正確
- [ ] originalText 不為空
- [ ] analysisResult.riskScore 是 1-10 的整數
- [ ] violations 是數組
- [ ] 每個 violation 包含：id, clause, riskLevel, reason, details
- [ ] totalViolations = len(violations)

#### Step 5：運行自動化測試
**動作**：執行 pytest 測試框架
```
執行：cd C:\contract-review-system\backend
pytest test_api.py -v
```

**完成標誌**：
- [ ] 所有測試執行完畢
- [ ] 列出每個測試的通過/失敗狀態
- [ ] 記錄失敗的測試（如果有）

#### Step 6：檢查日誌
**動作**：查看後端日誌了解整個流程
- 檢查 FastAPI 控制台輸出
- 檢查是否有錯誤信息
- 驗證 n8n webhook 調用成功

**完成標誌**：
- [ ] 日誌顯示完整的請求-響應流程
- [ ] 沒有 ERROR 級別日誌（WARNING 可接受）

### 時段 5 的驗證清單

**必須全部驗證通過：**
- [ ] 所有服務都在運行
- [ ] 測試 PDF 能成功上傳
- [ ] API 返回 200 狀態碼
- [ ] 返回的 JSON 結構完整且正確
- [ ] analysisResult 包含真實的分析結果
- [ ] pytest 測試無致命失敗
- [ ] 日誌顯示完整的流程

### ❌ 常見問題及對應

| 問題 | 症狀 | 對應 |
|------|------|------|
| 檔案上傳失敗 | 返回 400/500 | 檢查 PDF 格式和大小 |
| n8n 無回應 | API 超時 | 確認 n8n webhook 配置正確 |
| 返回結果為空 | analysisResult 為 {} | 檢查 n8n Code Node 邏輯 |
| 風險評分不合理 | riskScore 超過 10 或 < 1 | 檢查 Code Node 的評分計算 |
| 測試失敗 | pytest 返回 FAILED | 檢查 API 返回值是否符合測試預期 |

---

## 時段 6：前端開發（3:00-4:45 PM）

### 目標
開發 Vue 3 前端，能展示上傳頁面和分析結果

### 執行步驟

#### Step 1：初始化 Vue 3 項目
**動作**：創建 Vue 3 + Vite 項目
```
執行：npm create vite@latest contract-review-frontend -- --template vue
cd contract-review-frontend
npm install
```

**完成標誌**：
- [ ] 項目目錄已創建
- [ ] node_modules 已安裝
- [ ] package.json 存在

#### Step 2：安裝依賴包
**動作**：安裝需要的插件
```
執行：npm install vue-router axios tailwindcss postcss autoprefixer
```

**完成標誌**：
- [ ] 所有包安裝成功
- [ ] package.json 已更新

#### Step 3：配置路由
**動作**：設置兩個頁面間的導航
- 頁面 1：/ （上傳頁面）
- 頁面 2：/annotation （結果展示頁面）

**完成標誌**：
- [ ] router/index.js 已創建
- [ ] 路由配置正確
- [ ] 兩個頁面路由都能訪問

#### Step 4：開發上傳頁面
**動作**：創建 UploadPage.vue
- 功能：選擇 PDF、上傳、顯示 Loading
- 成功後導航到結果頁面

**完成標誌**：
- [ ] UploadPage.vue 已創建
- [ ] 能選擇 PDF 檔案
- [ ] 能上傳檔案（調用後端 API）
- [ ] 上傳成功後能導航到結果頁面
- [ ] 上傳失敗時能顯示錯誤信息

#### Step 5：開發結果展示頁面
**動作**：創建 AnnotationPage.vue
- 功能：顯示風險評分、違法條款、高亮原文

**完成標誌**：
- [ ] AnnotationPage.vue 已創建
- [ ] 能正確顯示 riskScore（1-10）
- [ ] 能列出 violations 數組
- [ ] 能正確高亮原文中的違法詞語
- [ ] 有「返回上傳」按鈕

#### Step 6：測試前端
**動作**：啟動開發服務器進行真實測試
```
執行：npm run dev
訪問：http://127.0.0.1:5173
```

**完整流程測試**：
1. 打開上傳頁面
2. 選擇測試 PDF
3. 點擊上傳
4. 查看是否正確導航到結果頁面
5. 驗證結果是否正確顯示

**完成標誌**：
- [ ] 前端能正常啟動
- [ ] 上傳頁面能正常顯示
- [ ] 能選擇 PDF 檔案
- [ ] 能上傳到後端 API
- [ ] 結果頁面能正確顯示
- [ ] 高亮功能工作正常

### 時段 6 的驗證清單

**必須全部驗證通過：**
- [ ] Vue 3 項目初始化成功
- [ ] 所有依賴安裝完成
- [ ] 路由配置正確
- [ ] UploadPage 功能完整
- [ ] AnnotationPage 功能完整
- [ ] 完整的上傳-分析-顯示流程能工作
- [ ] 沒有控制台錯誤（警告可接受）

### ❌ 常見問題及對應

| 問題 | 症狀 | 對應 |
|------|------|------|
| CORS 錯誤 | 瀏覽器報跨域錯誤 | 檢查後端 CORS 配置 |
| 檔案上傳失敗 | 顯示上傳錯誤 | 檢查 API URL 是否正確 |
| 路由失效 | 頁面導航不工作 | 檢查路由配置 |
| 樣式不顯示 | 頁面很醜陋 | 檢查 Tailwind CSS 配置 |
| 高亮不工作 | 原文沒有高亮 | 檢查高亮邏輯是否正確 |

---

## 時段 7：最終測試（4:45-5:00 PM）

### 目標
驗證整個系統端到端工作正常

### 執行步驟

#### Step 1：完整流程測試
**動作**：進行真實的完整測試
1. 打開前端：http://127.0.0.1:5173
2. 選擇測試 PDF 並上傳
3. 等待分析完成
4. 查看分析結果是否正確

**完成標誌**：
- [ ] 整個流程無報錯
- [ ] 最終結果正確顯示

#### Step 2：驗證所有達標條件
**動作**：檢查是否滿足所有要求

**檢查清單**：
- [ ] 時段 1 的所有條件都滿足
- [ ] 時段 2 的所有條件都滿足
- [ ] 時段 3 的所有條件都滿足
- [ ] 時段 5 的所有條件都滿足
- [ ] 時段 6 的所有條件都滿足

#### Step 3：記錄任何發現的問題
**動作**：如果發現 Bug 或不完美的地方，記錄下來
- Bug 描述
- 重現步驟
- 影響程度

**完成標誌**：
- [ ] 所有問題都已記錄

### 時段 7 的驗證清單

**必須確認**：
- [ ] 完整流程能工作
- [ ] 沒有致命 Bug
- [ ] 結果準確性可接受（允許 60% 準確度，A 版本期望值）

---

## 📊 Day 1 最終檢查清單

### ✅ 時段 1 完成標誌
- [ ] main.py 更新成功
- [ ] requirements.txt 安裝完成
- [ ] FastAPI 能啟動
- [ ] /health 端點返回 200
- [ ] /docs 能訪問
- [ ] test_api.py 能列出所有測試

### ✅ 時段 2 完成標誌
- [ ] Webhook URL 正常接收 POST
- [ ] HTTP Request 成功調用 Ollama
- [ ] Code Node 正確解析結果
- [ ] 完整工作流返回正確 JSON
- [ ] workflow_export.json 已保存

### ✅ 時段 3 完成標誌
- [ ] Dify 知識庫已創建
- [ ] 20 個消保法條款已上傳
- [ ] Embedding 完成（100%）
- [ ] 手動測試查詢返回準確結果
- [ ] Knowledge Base ID 已記錄

### ✅ 時段 5 完成標誌
- [ ] 所有服務都在運行
- [ ] 測試 PDF 上傳成功
- [ ] API 返回完整的 JSON
- [ ] analysisResult 包含真實分析結果
- [ ] pytest 測試通過（或記錄失敗原因）

### ✅ 時段 6 完成標誌
- [ ] Vue 3 項目初始化成功
- [ ] UploadPage 功能完整
- [ ] AnnotationPage 功能完整
- [ ] 完整流程能正常工作
- [ ] 沒有致命錯誤

### ✅ 時段 7 完成標誌
- [ ] 端到端流程驗證成功
- [ ] 所有時段的條件都滿足
- [ ] 所有發現的問題都已記錄

---

## 執行規則

### 每段完成後必須做的事

1. **通知你**：「時段 X 已完成，請驗證」
2. **列出驗證清單**：需要檢查的項目
3. **提供驗證方法**：如何驗證（curl 命令、UI 操作等）
4. **等待反饋**：確認所有項目都正確後再進行下一段
5. **如果有誤**：立即停止，報告錯誤，等待修正

### 禁止項目
- ❌ 不能假設某個階段成功
- ❌ 不能跳過任何驗證步驟
- ❌ 發現錯誤不能隱瞞
- ❌ 不能為了趕進度而放寬標準

---

## 開始執行

**準備好開始時段 1 嗎？**

確認以下事項後我們馬上開始：
- [ ] 你已閱讀本計畫
- [ ] 你理解了執行模式（真實執行 + 共同驗證）
- [ ] 你已準備好驗證每一段
- [ ] 你的環境已準備好（Docker、Python、Node.js 等）

**確認後，我們立即開始時段 1！** 🚀
