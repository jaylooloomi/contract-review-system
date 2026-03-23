"""
方案 1：pymupdf 內建 get_text("html")
特色：pymupdf 直接輸出 HTML，帶絕對定位，視覺上最接近原始 PDF 排版
缺點：絕對定位導致無法正常捲動，各頁面疊在一起
"""
import fitz

PDF = r"C:\contract-review-system\test\(佛光)合約管理系統維護合約書_V1.0_20260309.docx.pdf"
OUT = r"C:\contract-review-system\test\result1_pymupdf_html.html"

doc = fitz.open(PDF)
pages = []
for i, page in enumerate(doc):
    html = page.get_text("html")
    pages.append(f'<div class="page" id="page-{i}">{html}</div>')
doc.close()

wrapper = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body {{ font-family: serif; background: #f0f0f0; padding: 20px; }}
  .page {{
    background: white;
    margin: 0 auto 32px auto;
    max-width: 900px;
    padding: 40px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    position: relative;
    min-height: 400px;
    overflow: hidden;
  }}
</style>
</head><body>
{pages}
</body></html>"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(wrapper.format(pages="\n".join(pages)))

print(f"輸出：{OUT}")
