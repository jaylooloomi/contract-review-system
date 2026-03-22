import requests

url = "http://127.0.0.1:8000/api/analyze"
pdf_path = r"C:\contract-review-system\test\test_contract.pdf"

with open(pdf_path, "rb") as f:
    response = requests.post(url, files={"file": ("test_contract.pdf", f, "application/pdf")})

print("Status:", response.status_code)
print("Response:", response.json())
