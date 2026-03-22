import pdfplumber, requests, json

with pdfplumber.open(r"C:\contract-review-system\test\test_contract.pdf") as pdf:
    text = "\n\n".join(p.extract_text() for p in pdf.pages if p.extract_text())

payload = {
    "model": "minimax-m2:cloud",
    "prompt": f"分析以下合約，找出違反台灣消費者保護法的條款：\n\n{text}",
    "stream": False
}

print("送出文字長度:", len(text))
r = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=120)
print("Ollama 狀態:", r.status_code)
if r.status_code == 200:
    print("回應前200字:", r.json().get("response", "")[:200])
else:
    print("錯誤:", r.text[:200])
