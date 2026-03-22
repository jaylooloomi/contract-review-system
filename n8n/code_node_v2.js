// ============================================================
// n8n Code Node v2 — 修正版（相容 n8n v2 資料結構）
// ============================================================

// 1. 取得 Webhook 傳入的文字（試多個路徑）
const webhookJson = $node["Webhook"].json;
const inputText =
  webhookJson?.body?.text ||   // n8n v2 預設包一層 body
  webhookJson?.text ||          // n8n v1 / 某些設定
  webhookJson?.body?.body?.text ||
  "";

// 2. 取得 Ollama 回應文字（試多個路徑）
const ollamaJson = $node["HTTP Request"].json;
let responseText =
  ollamaJson?.response ||
  ollamaJson?.message?.content ||
  ollamaJson?.choices?.[0]?.message?.content ||
  "";

// 3. Debug 用（可看 n8n 執行結果確認取值）
// console.log("inputText:", inputText.slice(0, 100));
// console.log("responseText:", responseText.slice(0, 200));

// 4. 嘗試從 Ollama 回應解析結構化 JSON
let parsedResult = null;
const cleanText = responseText.replace(/```(?:json)?/g, "").replace(/```/g, "").trim();
try {
  parsedResult = JSON.parse(cleanText);
} catch (e) {
  const m = responseText.match(/\{[\s\S]*\}/);
  if (m) {
    try { parsedResult = JSON.parse(m[0]); } catch (e2) {}
  }
}

if (parsedResult && Array.isArray(parsedResult.violations)) {
  const violations = parsedResult.violations.map((v, i) => ({
    id: v.id || i + 1,
    clause: v.clause || v.條款 || "未知條款",
    riskLevel: v.riskLevel || v.風險等級 || "中",
    reason: v.reason || v.原因 || "違反消保法",
    details: v.details || v.詳細 || "",
  }));
  const score = Math.min(10, Math.max(1, Math.round(parsedResult.riskScore || calcScore(violations))));
  return [{ json: { violations, riskScore: score, totalViolations: violations.length, summary: parsedResult.summary || genSummary(violations, score) } }];
}

// 5. 備援：關鍵詞匹配（同時比對 inputText 和 responseText）
const searchText = inputText + " " + responseText;

const patterns = [
  { kws: ["概不退費","不得退款","不退款","不予退還","無法退費"], clause: "不合理退費條款", level: "高", reason: "違反消保法第19條", details: "消費者享有法定退費權利，企業不得以契約剝奪" },
  { kws: ["自動扣費","自動續約","自動扣款","自動繳費","自動延期"], clause: "自動扣費／自動續約條款", level: "高", reason: "違反消保法第17條", details: "需事先取得消費者明確書面同意" },
  { kws: ["概不負責","不負任何責任","免除一切責任","不承擔責任","不負責任"], clause: "全面免責條款", level: "高", reason: "違反消保法第7條", details: "不得以契約完全免除企業賠償責任" },
  { kws: ["責任限制","賠償上限","最高賠償","賠償不超過"], clause: "責任限制條款", level: "中", reason: "違反消保法第7條", details: "賠償上限不得低於消費者實際損害" },
  { kws: ["單方修改","隨時修改","有權修改","得修改條款","修改本合約"], clause: "單方修改條款", level: "高", reason: "違反消保法第12條", details: "不得單方面修改契約，需事先通知消費者" },
  { kws: ["強制仲裁","不得提起訴訟","放棄訴訟","不得訴訟"], clause: "強制仲裁條款", level: "高", reason: "違反消保法第10條", details: "消費者不得被強制放棄訴訟權利" },
  { kws: ["提供第三方","資料共享","資料轉讓","出售個人資料"], clause: "個人資料共享條款", level: "中", reason: "違反個資法第7條", details: "需有明確告知與當事人同意" },
];

const violations = [];
for (const p of patterns) {
  if (p.kws.some(kw => searchText.includes(kw))) {
    violations.push({ id: violations.length + 1, clause: p.clause, riskLevel: p.level, reason: p.reason, details: p.details });
  }
}

const score = calcScore(violations);
return [{ json: { violations, riskScore: score, totalViolations: violations.length, summary: genSummary(violations, score) } }];

// ── 輔助函式 ──
function calcScore(v) {
  if (!v.length) return 1;
  let s = 0;
  for (const x of v) s += x.riskLevel === "高" ? 3 : x.riskLevel === "中" ? 2 : 1;
  return Math.min(10, Math.max(1, s));
}
function genSummary(v, s) {
  if (!v.length) return `本合約未偵測到明顯違法條款，風險評分 ${s}/10。`;
  return `本合約共偵測到 ${v.length} 個疑似違法條款，風險評分 ${s}/10。建議簽署前諮詢專業人士。`;
}
