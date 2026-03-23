"""
方案 4：pdfplumber 提取文字 + 字元位置重建排版
特色：pdfplumber 可取得每個字元的精確座標，用來重建對齊
缺點：速度較慢，對複雜排版還原度有限
"""
import pdfplumber
import html as html_module

PDF = r"C:\contract-review-system\test\(佛光)合約管理系統維護合約書_V1.0_20260309.docx.pdf"
OUT = r"C:\contract-review-system\test\result4_pdfplumber.html"

pages_html = []

with pdfplumber.open(PDF) as pdf:
    for page_num, page in enumerate(pdf.pages):
        page_width = float(page.width)
        words = page.extract_words(x_tolerance=3, y_tolerance=3, keep_blank_chars=False)

        if not words:
            pages_html.append(f'<div class="pdf-page" id="page-{page_num}"><div class="page-label">第 {page_num+1} 頁（無文字）</div></div>')
            continue

        # 依 y 座標分組成行（y 差距 < 5 視為同行）
        lines = []
        current_line = [words[0]]
        for word in words[1:]:
            if abs(word["top"] - current_line[0]["top"]) < 5:
                current_line.append(word)
            else:
                lines.append(current_line)
                current_line = [word]
        lines.append(current_line)

        page_html = f'<div class="pdf-page" id="page-{page_num}"><div class="page-label">第 {page_num+1} 頁</div>'
        for line_words in lines:
            line_words.sort(key=lambda w: w["x0"])
            # 用第一個字的 x0 推算縮排
            x0 = line_words[0]["x0"]
            indent_pct = (x0 / page_width) * 100
            line_text = " ".join(html_module.escape(w["text"]) for w in line_words)
            page_html += f'<p class="line" style="margin-left:{indent_pct:.1f}%">{line_text}</p>'
        page_html += '</div>'
        pages_html.append(page_html)

css = """
body { font-family: serif; background: #f0f0f0; padding: 20px; }
.pdf-page {
  background: white; max-width: 900px; margin: 0 auto 32px auto;
  padding: 48px 56px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.page-label { font-size: 10pt; color: #aaa; margin-bottom: 16px; text-align: right; }
.line { margin: 0; line-height: 1.8; font-size: 12pt; }
"""

html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>' + "\n".join(pages_html) + '</body></html>'

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"輸出：{OUT}，{len(pages_html)} 頁")
