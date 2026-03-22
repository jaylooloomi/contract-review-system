// ============================================================
// n8n Code Node — Multi Law Retrieval
// 1. 解析合約分類節點輸出
// 2. 依法律清單查詢多個 Dify 知識庫
// 3. 合併法條回傳給 Ollama 分析節點
// ============================================================

const DATASET_MAP = {
  "taiwan_consumer_protection_law": "44e5a632-35e1-4669-b3a8-545828d75d53",
  "taiwan_civil_law":               "0563691d-73ab-479f-aa48-70bf26a77112",
  "taiwan_labor_law":               "d6460675-fcdc-4c56-8041-04787bcf5aca",
  "taiwan_privacy_law":             "5176b708-a715-4e27-82bb-d0100044c88c",
  "taiwan_company_law":             "b809f5ea-9248-4376-9f09-0677c4614de6",
};

const DIFY_API_KEY  = "dataset-BH63uXTBsTfMX1tvPBl3H4Fd";
const DIFY_BASE_URL = "http://127.0.0.1:3001";

// 1. 取得合約文字
const contractText = $node["Webhook"].json.body?.text || $node["Webhook"].json.text || "";

// 2. 解析分類節點輸出
const classifierRaw = $node["Contract Classifier"].json;
let classifierResponse = classifierRaw?.response || classifierRaw?.message?.content || "";

let classification = { contractType: "一般合約", laws: ["taiwan_consumer_protection_law"] };
try {
  const clean = classifierResponse.replace(/```(?:json)?/g, "").replace(/```/g, "").trim();
  const m = clean.match(/\{[\s\S]*\}/);
  if (m) classification = JSON.parse(m[0]);
} catch (e) {}

const laws = Array.isArray(classification.laws) && classification.laws.length > 0
  ? classification.laws.slice(0, 3)
  : ["taiwan_consumer_protection_law"];

// 3. 查詢各知識庫
const allChunks = [];
for (const law of laws) {
  const datasetId = DATASET_MAP[law];
  if (!datasetId) continue;
  try {
    const response = await $helpers.httpRequest({
      method: "POST",
      url: `${DIFY_BASE_URL}/v1/datasets/${datasetId}/retrieve`,
      headers: {
        "Authorization": `Bearer ${DIFY_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: contractText.substring(0, 500), top_k: 2 }),
    });
    if (response.records) {
      for (const record of response.records) {
        const content = record.segment?.content || "";
        if (content) allChunks.push(`【${law}】\n${content}`);
      }
    }
  } catch (e) {
    // 跳過查詢失敗的知識庫
  }
}

const retrievedLaws = allChunks.join("\n\n---\n\n") || "（知識庫查詢無結果）";

return [{
  json: {
    contractType:  classification.contractType,
    appliedLaws:   laws,
    retrievedLaws: retrievedLaws,
    contractText:  contractText,
  }
}];
