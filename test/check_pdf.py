import pdfplumber
pdf = pdfplumber.open(r"C:\contract-review-system\test\test_contract.pdf")
text = pdf.pages[0].extract_text()
print("Text:", repr(text))
print("Length:", len(text) if text else 0)
