import pdfplumber
pdf = pdfplumber.open(r"C:\contract-review-system\test\test_contract.pdf")
text = pdf.pages[0].extract_text()
# 確認是否含中文關鍵字
keywords = ["退費", "責任", "自動", "租客", "房東", "Refund", "Liability"]
found = [k for k in keywords if k in (text or "")]
print("找到關鍵字:", found)
print("前50字元 bytes:", text[:50].encode("utf-8") if text else "None")
