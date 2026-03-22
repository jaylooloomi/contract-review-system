from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 使用 Windows 內建中文字體
font_paths = [
    r"C:\Windows\Fonts\msjh.ttc",       # 微軟正黑體
    r"C:\Windows\Fonts\mingliu.ttc",    # 細明體
    r"C:\Windows\Fonts\simsun.ttc",     # 新細明體
    r"C:\Windows\Fonts\kaiu.ttf",       # 標楷體
]

font_name = None
for fp in font_paths:
    if os.path.exists(fp):
        try:
            pdfmetrics.registerFont(TTFont("ChineseFont", fp))
            font_name = "ChineseFont"
            print(f"使用字體: {fp}")
            break
        except:
            continue

if not font_name:
    print("找不到中文字體，改用英文測試內容")
    font_name = "Helvetica"

pdf_path = r"C:\contract-review-system\test\test_contract.pdf"
c = canvas.Canvas(pdf_path, pagesize=A4)
c.setFont(font_name, 12)

if font_name == "Helvetica":
    lines = [
        "Rental Contract",
        "",
        "Article 1: No Refund - Tenant cannot request any refund under any circumstances.",
        "",
        "Article 2: No Liability - Landlord bears no responsibility for any damages.",
        "",
        "Article 3: Auto Deduction - Landlord may deduct fees without prior notice.",
    ]
else:
    lines = [
        "租屋合約書",
        "",
        "第一條 退費條款：租客不得要求退款，無論任何原因。",
        "",
        "第二條 責任限制：房東對任何損失概不負責，包括財產損失及人身傷害。",
        "",
        "第三條 自動扣費：房東有權在未通知租客的情況下自動扣取費用。",
        "",
        "第四條 合約修改：房東可單方面修改本合約，無需通知租客。",
    ]

y = 750
for line in lines:
    c.drawString(50, y, line)
    y -= 30

c.save()
print(f"PDF 建立成功：{pdf_path}")
