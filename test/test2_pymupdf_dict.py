"""
方案 2：pymupdf get_text("dict") 自組 HTML（目前系統使用的方法）
特色：正常文字流排版，保留字體大小/粗體/斜體
缺點：不保留縮排、表格、欄位對齊
"""
import fitz
import html as html_module

PDF = r"C:\contract-review-system\test\(佛光)合約管理系統維護合約書_V1.0_20260309.docx.pdf"
OUT = r"C:\contract-review-system\test\result2_pymupdf_dict.html"

doc = fitz.open(PDF)
pages_html = []

for page_num, page in enumerate(doc):
    blocks = page.get_text("dict")["blocks"]
    page_html = f'<div class="pdf-page" id="page-{page_num}"><div class="page-label">第 {page_num+1} 頁</div>'
    for block_num, block in enumerate(blocks):
        if block.get("type") != 0:
            continue
        block_html = f'<div class="pdf-block">'
        for line in block.get("lines", []):
            line_html = '<p class="pdf-line">'
            for span in line.get("spans", []):
                text = html_module.escape(span.get("text", ""))
                size = span.get("size", 12)
                flags = span.get("flags", 0)
                bold = "font-weight:bold;" if flags & (1 << 4) else ""
                italic = "font-style:italic;" if flags & (1 << 1) else ""
                color_int = span.get("color", 0)
                r = (color_int >> 16) & 0xFF
                g = (color_int >> 8) & 0xFF
                b = color_int & 0xFF
                color = f"color:rgb({r},{g},{b});" if color_int != 0 else ""
                style = f"font-size:{size:.1f}pt;{bold}{italic}{color}"
                line_html += f'<span style="{style}">{text}</span>'
            line_html += '</p>'
            block_html += line_html
        block_html += '</div>'
        page_html += block_html
    page_html += '</div>'
    pages_html.append(page_html)

doc.close()

css = """
body { font-family: serif; background: #f0f0f0; padding: 20px; }
.pdf-page {
  background: white; max-width: 900px; margin: 0 auto 32px auto;
  padding: 48px 56px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.page-label { font-size: 10pt; color: #aaa; margin-bottom: 16px; text-align: right; }
.pdf-block { margin-bottom: 8px; }
.pdf-line { margin: 0; line-height: 1.8; }
"""

html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>' + "\n".join(pages_html) + '</body></html>'

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"輸出：{OUT}，{len(pages_html)} 頁")
