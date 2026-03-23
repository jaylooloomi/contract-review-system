# Dify 知識庫安裝 SOP（新用戶）

## 前置條件

- Docker Desktop 已啟動
- Dify 服務已啟動（`http://127.0.0.1:3001` 可開啟）
- Ollama 已啟動，且已安裝 `nomic-embed-text`：
  ```cmd
  ollama pull nomic-embed-text
  ```

---

## Step 1 — 登入 Dify

開啟瀏覽器，前往 `http://127.0.0.1:3001`，登入帳號。

---

## Step 2 — 建立 Dataset API Key

1. 點選右上角帳號 → **Settings**
2. 左側選單選 **API Keys**（或 **Datasets API**）
3. 點選 **「Create new secret key」**
4. 複製 API Key（格式：`dataset-xxxxxxxxxxxxxxxxxxxxxxxx`）

---

## Step 3 — 執行自動初始化腳本

在專案根目錄執行：

```cmd
python dify/setup.py
```

輸入剛才複製的 API Key，腳本會自動：
- 建立 5 個知識庫（消保法、民法、勞基法、個資法、公司法）
- 上傳對應 PDF 檔案
- 等待 embedding 完成
- 更新 `dify/dataset_ids.md`

> 首次執行約需 5～15 分鐘（視 PDF 大小與 Ollama 速度）

---

## Step 4 — 更新 n8n Multi Law Retrieval 節點

腳本執行完畢後，終端機會輸出新的 Dataset IDs：

```
taiwan_consumer_protection_law    xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
taiwan_civil_law                  xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
taiwan_labor_law                  xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
taiwan_privacy_law                xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
taiwan_company_law                xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

前往 n8n（`http://127.0.0.1:5678`），開啟 **Contract Analysis** workflow，找到 **Multi Law Retrieval** 節點，將 `DATASET_MAP` 與 `DIFY_API_KEY` 更新為你的值：

```js
const DATASET_MAP = {
  "taiwan_consumer_protection_law": "你的 ID",
  "taiwan_civil_law":               "你的 ID",
  "taiwan_labor_law":               "你的 ID",
  "taiwan_privacy_law":             "你的 ID",
  "taiwan_company_law":             "你的 ID",
};
const DIFY_API_KEY  = "dataset-你的 API Key";
const DIFY_BASE_URL = "http://127.0.0.1:3001";
```

儲存並啟用 workflow。

---

## 確認完成

上傳一份測試合約至前端（`http://127.0.0.1:5173`），確認：
- 分析結果有回傳違法條款
- 每張卡片顯示風險等級與法條依據
