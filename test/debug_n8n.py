import pdfplumber
import requests
import json

# 提取 PDF 文字
with pdfplumber.open(r"C:\contract-review-system\test\test_contract.pdf") as pdf:
    text = "\n\n".join(p.extract_text() for p in pdf.pages if p.extract_text())

print("提取文字長度:", len(text))
print("前100字:", text[:100])
print()

# 直接送 n8n
payload = {"text": text, "filename": "test_contract.pdf"}
r = requests.post("http://localhost:5678/webhook/analyze",
                  json=payload,
                  timeout=120)
print("n8n 回應狀態:", r.status_code)
print("n8n 回應:", json.dumps(r.json(), ensure_ascii=False, indent=2)[:500])
