"""
方案 3：pymupdf get_text("blocks") + 位置資訊模擬縮排
特色：利用 bbox 的 x 座標推算縮排量，讓段落對齊更接近原始排版
缺點：仍是文字流，無法完美還原複雜表格
"""
import fitz
import html as html_module

PDF = r"C:\contract-review-system\test\(佛光)合約管理系統維護合約書_V1.0_20260309.docx.pdf"
OUT = r"C:\contract-review-system\test\result3_pymupdf_blocks.html"

doc = fitz.open(PDF)
pages_html = []

for page_num, page in enumerate(doc):
    page_width = page.rect.width
    blocks = page.get_text("dict")["blocks"]
    page_html = f'<div class="pdf-page" id="page-{page_num}"><div class="page-label">第 {page_num+1} 頁</div>'

    for block in blocks:
        if block.get("type") != 0:
            continue
        # 用 bbox x0 推算左側縮排百分比
        x0 = block["bbox"][0]
        indent_pct = (x0 / page_width) * 100
        indent_style = f"margin-left:{indent_pct:.1f}%;"

        block_html = f'<div class="pdf-block" style="{indent_style}">'
        for line in block.get("lines", []):
            line_html = '<p class="pdf-line">'
            for span in line.get("spans", []):
                text = html_module.escape(span.get("text", ""))
                size = span.get("size", 12)
                flags = span.get("flags", 0)
                bold = "font-weight:bold;" if flags & (1 << 4) else ""
                italic = "font-style:italic;" if flags & (1 << 1) else ""
                style = f"font-size:{size:.1f}pt;{bold}{italic}"
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
.pdf-block { margin-bottom: 6px; }
.pdf-line { margin: 0; line-height: 1.8; }
"""

html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>' + "\n".join(pages_html) + '</body></html>'

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"輸出：{OUT}，{len(pages_html)} 頁")
