// ============================================================
// n8n Code Node — 合約分析結果解析器
// 將 Ollama (minimax-m2:cloud) 的回應轉換為結構化 JSON
// ============================================================

// 1. 取得上游 HTTP Request 節點的資料
const ollamaRaw = $node["HTTP Request"].json;
const inputText = $node["Webhook"].json.body?.text || $node["Webhook"].json.text || "";

// 2. 提取 Ollama 回應文字
let responseText = "";
if (ollamaRaw && ollamaRaw.response) {
  responseText = ollamaRaw.response;
} else if (ollamaRaw && ollamaRaw.message && ollamaRaw.message.content) {
  responseText = ollamaRaw.message.content;
} else if (typeof ollamaRaw === "string") {
  responseText = ollamaRaw;
}

// 3. 嘗試從回應中解析 JSON（移除 Markdown code block）
let parsedResult = null;

// 嘗試解析方法 A：直接 JSON.parse
try {
  parsedResult = JSON.parse(responseText);
} catch (e) {
  // 嘗試解析方法 B：從 Markdown code block 中提取 JSON
  const jsonMatch = responseText.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (jsonMatch) {
    try {
      parsedResult = JSON.parse(jsonMatch[1].trim());
    } catch (e2) {
      // 繼續嘗試備援方案
    }
  }
}

// 4. 若 JSON 解析成功，直接使用結構化結果
if (
  parsedResult &&
  Array.isArray(parsedResult.violations)
) {
  const violations = parsedResult.violations.map((v, i) => ({
    id: v.id || i + 1,
    clause: v.clause || v.條款 || v.name || "未知條款",
    riskLevel: v.riskLevel || v.risk_level || v.風險等級 || "中",
    reason: v.reason || v.原因 || "違反消保法",
    details: v.details || v.詳細 || v.description || "",
  }));

  const riskScore = parsedResult.riskScore || parsedResult.risk_score || calculateScore(violations);
  const clampedScore = Math.min(10, Math.max(1, Math.round(riskScore)));

  return {
    violations,
    riskScore: clampedScore,
    totalViolations: violations.length,
    summary: parsedResult.summary || generateSummary(violations, clampedScore),
  };
}

// 5. 備援方案：關鍵詞匹配（當 LLM 未回傳結構化 JSON 時）
const violationPatterns = [
  {
    keywords: ["概不退費", "不得退款", "不退款", "不予退還", "無法退費"],
    clause: "不合理退費條款",
    riskLevel: "高",
    reason: "違反消保法第 19 條（通訊購物 7 日鑑賞期）及第 11 條（不公平條款無效）",
    details: "消費者享有法定退費權利，企業不得以契約完全剝奪退費權利",
  },
  {
    keywords: ["自動扣費", "自動續約", "自動扣款", "自動繳費", "自動延期"],
    clause: "自動扣費／自動續約條款",
    riskLevel: "高",
    reason: "違反消保法第 17 條（標準契約應載明事項）及公平交易法",
    details: "自動扣費需事先取得消費者明確同意，並提供取消機制",
  },
  {
    keywords: ["概不負責", "不負任何責任", "免除一切責任", "不承擔責任", "概不承擔"],
    clause: "全面免責條款",
    riskLevel: "高",
    reason: "違反消保法第 7 條（企業不得以契約免除其應負之責任）",
    details: "企業對其商品或服務造成的損害，不得完全免除賠償責任",
  },
  {
    keywords: ["責任限制", "賠償上限", "最高賠償", "賠償不超過"],
    clause: "責任限制條款",
    riskLevel: "中",
    reason: "違反消保法第 7 條（責任限制需合理且不得低於法定標準）",
    details: "賠償上限設定需合理，不得低於消費者實際損害",
  },
  {
    keywords: ["單方修改", "隨時修改", "有權修改", "得修改條款", "修改本合約"],
    clause: "單方修改條款",
    riskLevel: "高",
    reason: "違反消保法第 12 條（不公平標準契約條款無效）",
    details: "企業不得單方面修改契約，需事先通知並取得消費者同意",
  },
  {
    keywords: ["個人資料", "蒐集資料", "提供第三方", "資料共享", "資料轉讓"],
    clause: "個人資料處理條款",
    riskLevel: "中",
    reason: "可能違反個人資料保護法第 7 條（須有明確告知與同意）",
    details: "蒐集、處理、利用個人資料需有明確法律依據並取得當事人同意",
  },
  {
    keywords: ["仲裁", "不得提起訴訟", "放棄訴訟權", "強制仲裁"],
    clause: "強制仲裁／放棄訴訟條款",
    riskLevel: "高",
    reason: "違反消保法第 10 條（消費者申訴及爭議處理權利）",
    details: "消費者有權選擇訴訟途徑，不得被強制放棄訴訟權利",
  },
  {
    keywords: ["隱私權政策", "Cookie", "追蹤", "行為分析"],
    clause: "隱私追蹤條款",
    riskLevel: "低",
    reason: "需符合個人資料保護法第 8 條告知義務",
    details: "應明確告知追蹤範圍、用途及消費者選擇退出的方式",
  },
];

// 執行關鍵詞匹配
const violations = [];
for (const pattern of violationPatterns) {
  const found = pattern.keywords.some(
    (kw) => inputText.includes(kw) || responseText.includes(kw)
  );
  if (found) {
    violations.push({
      id: violations.length + 1,
      clause: pattern.clause,
      riskLevel: pattern.riskLevel,
      reason: pattern.reason,
      details: pattern.details,
    });
  }
}

// 6. 計算風險評分
const riskScore = calculateScore(violations);

return {
  violations,
  riskScore,
  totalViolations: violations.length,
  summary: generateSummary(violations, riskScore),
};

// ── 輔助函式 ──────────────────────────────────────────────────

function calculateScore(violations) {
  if (violations.length === 0) return 1;
  let score = 0;
  for (const v of violations) {
    if (v.riskLevel === "高") score += 3;
    else if (v.riskLevel === "中") score += 2;
    else score += 1;
  }
  return Math.min(10, Math.max(1, score));
}

function generateSummary(violations, score) {
  if (violations.length === 0) {
    return "本合約未偵測到明顯違法條款，風險評分 1/10。建議仍諮詢法律專業人士確認。";
  }
  const highCount = violations.filter((v) => v.riskLevel === "高").length;
  const midCount = violations.filter((v) => v.riskLevel === "中").length;
  const lowCount = violations.filter((v) => v.riskLevel === "低").length;

  let levelDesc = "";
  if (highCount > 0) levelDesc += `高風險 ${highCount} 項、`;
  if (midCount > 0) levelDesc += `中風險 ${midCount} 項、`;
  if (lowCount > 0) levelDesc += `低風險 ${lowCount} 項、`;
  levelDesc = levelDesc.replace(/、$/, "");

  return `本合約共偵測到 ${violations.length} 個疑似違法條款（${levelDesc}），風險評分 ${score}/10。建議在簽署前諮詢消費者保護委員會或法律專業人士。`;
}
