import os
import logging
import httpx
import pdfplumber
from datetime import datetime
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import io

load_dotenv()

# ── 日誌設定 ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("contract-review")

# ── 設定 ────────────────────────────────────────────────────────────────────
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://127.0.0.1:5678/webhook/analyze")
MAX_FILE_SIZE_MB = 20

# ── FastAPI 應用程式 ─────────────────────────────────────────────────────────
app = FastAPI(
    title="台灣消費者合約審閱系統 API",
    description="上傳 PDF 合約，自動偵測違反台灣消保法的條款",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 工具函式 ─────────────────────────────────────────────────────────────────
def extract_text_from_pdf(file_bytes: bytes) -> str:
    """使用 pdfplumber 從 PDF 提取文字"""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages_text = []
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    pages_text.append(text.strip())
                logger.info(f"PDF 第 {i+1} 頁提取完成，字元數: {len(text) if text else 0}")
            full_text = "\n\n".join(pages_text)
            logger.info(f"PDF 全文提取完成，共 {len(full_text)} 字元，{len(pdf.pages)} 頁")
            return full_text
    except Exception as e:
        logger.error(f"PDF 提取失敗: {e}")
        raise HTTPException(status_code=422, detail=f"無法解析 PDF 檔案: {str(e)}")


REGION_LABEL = {
    "taiwan": "台灣消費者保護法",
    "china": "中國消費者權益保護法",
    "cross": "兩岸相關法規（台灣消保法及中國消費者權益保護法）",
    "usa": "美國聯邦消費者保護法（FTC Act、CCPA 等）",
}


async def call_n8n_webhook(text: str, filename: str, region: str = "taiwan") -> dict:
    """呼叫 n8n webhook 進行合約分析"""
    # 將換行符轉為空格，避免 n8n raw JSON body 因換行而失效
    clean_text = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    region_label = REGION_LABEL.get(region, REGION_LABEL["taiwan"])
    payload = {"text": clean_text, "filename": filename, "region": region, "regionLabel": region_label}
    logger.info(f"呼叫 n8n webhook: {N8N_WEBHOOK_URL}")
    logger.info(f"傳送文字長度: {len(text)} 字元")

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(N8N_WEBHOOK_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(f"n8n webhook 回應成功，狀態碼: {response.status_code}")
            logger.info(f"分析結果 - violations: {result.get('totalViolations', '?')} 個，riskScore: {result.get('riskScore', '?')}")
            return result
        except httpx.TimeoutException:
            logger.error("n8n webhook 呼叫逾時（120秒）")
            raise HTTPException(status_code=504, detail="分析服務逾時，請確認 n8n 服務正常運行")
        except httpx.HTTPStatusError as e:
            logger.error(f"n8n webhook 回應錯誤: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=502, detail=f"分析服務回應錯誤: {e.response.status_code}")
        except httpx.ConnectError:
            logger.error(f"無法連線到 n8n webhook: {N8N_WEBHOOK_URL}")
            raise HTTPException(status_code=503, detail="無法連線到分析服務，請確認 n8n 服務正常運行")


# ── API 端點 ─────────────────────────────────────────────────────────────────
@app.get("/health", summary="健康檢查")
async def health_check():
    """確認服務是否正常運行"""
    logger.info("收到 health check 請求")
    return {
        "status": "healthy",
        "service": "contract-review-backend",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/analyze", summary="分析合約 PDF")
async def analyze_contract(
    file: UploadFile = File(..., description="要分析的合約 PDF 檔案"),
    region: str = Form("taiwan", description="適用法規地區（taiwan/china/cross/usa）"),
):
    """
    接收 PDF 合約檔案，提取文字後透過 n8n + Ollama 分析違法條款。

    - **file**: PDF 格式的合約檔案（multipart/form-data）
    - 回傳分析結果，包含違法條款列表和風險評分
    """
    logger.info(f"收到分析請求，檔名: {file.filename}, 內容類型: {file.content_type}")

    # 檔案類型驗證
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        logger.warning(f"上傳了非 PDF 檔案: {file.filename}")
        raise HTTPException(status_code=400, detail="只接受 PDF 格式的檔案")

    # 讀取檔案內容
    file_bytes = await file.read()
    file_size_mb = len(file_bytes) / (1024 * 1024)
    logger.info(f"檔案大小: {file_size_mb:.2f} MB")

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="上傳的檔案是空的")

    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"檔案大小超過限制（最大 {MAX_FILE_SIZE_MB} MB）")

    # 提取 PDF 文字
    logger.info("開始提取 PDF 文字...")
    original_text = extract_text_from_pdf(file_bytes)

    if not original_text.strip():
        logger.warning("PDF 提取的文字為空，可能是掃描版 PDF 或加密 PDF")
        raise HTTPException(status_code=422, detail="無法從 PDF 中提取文字，可能是掃描版或加密 PDF")

    # 呼叫 n8n 分析
    logger.info("開始呼叫 n8n 進行分析...")
    analysis_result = await call_n8n_webhook(original_text, file.filename, region)

    response_data = {
        "success": True,
        "filename": file.filename,
        "originalText": original_text,
        "analysisResult": analysis_result,
        "timestamp": datetime.now().isoformat(),
    }

    logger.info(f"分析完成，回傳結果給前端")
    return response_data


# ── 啟動入口 ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    logger.info(f"啟動服務，n8n webhook URL: {N8N_WEBHOOK_URL}")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
