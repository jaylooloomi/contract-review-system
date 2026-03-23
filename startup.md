# 合約審查系統 - 啟動指南

## 前置需求

請確認以下軟體已安裝：

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Node.js](https://nodejs.org/) v18+
- [Python](https://www.python.org/) 3.10+
- [Ollama](https://ollama.com/)
- n8n：`npm install -g n8n`

---

## 啟動服務（透過 Claude Code / Desktop Commander）

依序執行以下指令，每個服務在獨立背景 process 中執行。

### 1. Docker Desktop
```
"C:\Program Files\Docker\Docker\Docker Desktop.exe"
```
> 等待 Docker engine 就緒後再繼續。

### 2. 確認 pdf2htmlEX image
```cmd
docker image inspect iapain/pdf2htmlex || docker pull iapain/pdf2htmlex
```

### 3. Dify
```cmd
cd /d C:\dify\dify\docker && docker compose up
```

### 4. Ollama
```cmd
ollama serve
```

### 5. n8n
```cmd
n8n start
```

### 6. FastAPI Backend
```cmd
cd /d C:\contract-review-system\backend && python main.py
```

### 7. Vue Frontend
```cmd
cd /d C:\contract-review-system\frontend && npm run dev
```

---

## 服務端口

| 服務         | URL                         |
|--------------|-----------------------------|
| Frontend     | http://127.0.0.1:5173       |
| Backend API  | http://127.0.0.1:8000/docs  |
| n8n          | http://127.0.0.1:5678       |
| Ollama       | http://127.0.0.1:11434      |
| Dify         | http://127.0.0.1:3001       |

---

## AI 指令：啟動完成後請輸出

所有服務啟動完畢後，AI 必須輸出以下服務狀態表格：

| 服務         | URL                         |
|--------------|-----------------------------|
| Frontend     | http://127.0.0.1:5173       |
| Backend API  | http://127.0.0.1:8000/docs  |
| n8n          | http://127.0.0.1:5678       |
| Ollama       | http://127.0.0.1:11434      |
| Dify         | http://127.0.0.1:3001       |
