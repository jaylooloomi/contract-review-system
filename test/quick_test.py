import requests, json
r = requests.post(
    'http://127.0.0.1:8000/api/analyze',
    files={'file': open(r'C:\contract-review-system\test\test_contract.pdf', 'rb')},
    timeout=120
)
data = r.json()
print("riskScore:", data['analysisResult']['riskScore'])
print("totalViolations:", data['analysisResult']['totalViolations'])
print("summary:", data['analysisResult']['summary'])
print()
for v in data['analysisResult']['violations']:
    print(f"[{v['riskLevel']}風險] {v['clause']}")
    print(f"  原因: {v['reason'][:50]}...")
    print()
