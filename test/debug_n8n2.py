import requests, json

# 測試不同的輸入
tests = [
    ("短文字（之前可以）", "第一條 退費條款：租客不得退款。第二條 責任限制：房東無責任。"),
    ("含換行的文字", "租屋合約書\n\n第一條 退費條款：租客不得退款。\n\n第二條 責任限制：房東無責任。"),
    ("4條完整內容", "租屋合約書\n\n第一條 退費條款：租客不得要求退款，無論任何原因。\n\n第二條 責任限制：房東對任何損失概不負責。\n\n第三條 自動扣費：房東有權在未通知租客的情況下自動扣取費用。\n\n第四條 合約修改：房東可單方面修改本合約。"),
]

for name, text in tests:
    print(f"\n=== 測試: {name} (長度:{len(text)}) ===")
    r = requests.post("http://localhost:5678/webhook/analyze",
                      json={"text": text, "filename": "test.pdf"},
                      timeout=120)
    print(f"狀態: {r.status_code}")
    if r.status_code == 200:
        d = r.json()
        print(f"violations: {d.get('totalViolations')}, score: {d.get('riskScore')}")
    else:
        print(f"錯誤: {r.text[:100]}")
