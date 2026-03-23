"""
dify/setup.py — 自動初始化 Dify 知識庫

使用方式：
    python dify/setup.py

執行後會：
1. 建立 5 個知識庫
2. 上傳對應的 PDF / MD 檔案
3. 等待 embedding 完成
4. 輸出新的 Dataset IDs，更新 dify/dataset_ids.md
"""

import os
import sys
import json
import time
import requests

# Windows 終端機 UTF-8 輸出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ──────────────────────────────────────────────
# 設定
# ──────────────────────────────────────────────
DIFY_URL = "http://127.0.0.1:3001"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LAW_DIR = os.path.join(SCRIPT_DIR, "law.moj.gov.tw")

# 知識庫定義：name → 要上傳的檔案列表
DATASETS = [
    {
        "name": "taiwan_consumer_protection_law",
        "description": "台灣消費者保護法相關條文與知識庫",
        "files": [
            os.path.join(LAW_DIR, "消費者保護法.pdf"),
            os.path.join(SCRIPT_DIR, "taiwan_cpa_knowledge.md"),
        ],
    },
    {
        "name": "taiwan_civil_law",
        "description": "台灣民法相關條文",
        "files": [
            os.path.join(LAW_DIR, "民法.pdf"),
        ],
    },
    {
        "name": "taiwan_labor_law",
        "description": "台灣勞動基準法相關條文",
        "files": [
            os.path.join(LAW_DIR, "勞動基準法.pdf"),
        ],
    },
    {
        "name": "taiwan_privacy_law",
        "description": "台灣個人資料保護法相關條文",
        "files": [
            os.path.join(LAW_DIR, "個人資料保護法.pdf"),
        ],
    },
    {
        "name": "taiwan_company_law",
        "description": "台灣公司法相關條文",
        "files": [
            os.path.join(LAW_DIR, "公司法.pdf"),
        ],
    },
]

UPLOAD_SETTINGS = {
    "indexing_technique": "high_quality",
    "process_rule": {"mode": "automatic"},
}


# ──────────────────────────────────────────────
# API helpers
# ──────────────────────────────────────────────
def api(method, path, api_key, **kwargs):
    headers = {"Authorization": f"Bearer {api_key}"}
    r = requests.request(method, f"{DIFY_URL}/v1{path}", headers=headers, **kwargs)
    r.raise_for_status()
    return r.json()


def list_all_datasets(api_key):
    """取得所有已存在的知識庫"""
    result = {}
    page = 1
    while True:
        data = api("GET", f"/datasets?page={page}&limit=100", api_key)
        for ds in data.get("data", []):
            result[ds["name"]] = ds["id"]
        if not data.get("has_more"):
            break
        page += 1
    return result


def create_dataset(name, description, api_key, existing: dict):
    """建立知識庫，若已存在則直接回傳現有 ID"""
    if name in existing:
        print(f"(已存在，跳過建立)", end=" ")
        return {"id": existing[name]}
    return api("POST", "/datasets", api_key, json={
        "name": name,
        "description": description,
        "indexing_technique": "high_quality",
        "permission": "only_me",
    })


def upload_file(dataset_id, filepath, api_key):
    filename = os.path.basename(filepath)
    mime = "text/markdown" if filepath.endswith(".md") else "application/pdf"
    with open(filepath, "rb") as f:
        return api(
            "POST",
            f"/datasets/{dataset_id}/document/create-by-file",
            api_key,
            files={"file": (filename, f, mime)},
            data={"data": json.dumps(UPLOAD_SETTINGS)},
        )


def wait_for_indexing(dataset_id, api_key, timeout=300):
    """等待知識庫所有文件 embedding 完成"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        docs = api("GET", f"/datasets/{dataset_id}/documents?page=1&limit=20", api_key)
        statuses = [d.get("indexing_status") for d in docs.get("data", [])]
        if statuses and all(s == "completed" for s in statuses):
            return True
        pending = [s for s in statuses if s != "completed"]
        print(f"      ⏳ 等待 embedding... 狀態: {pending}", end="\r")
        time.sleep(5)
    return False


def update_dataset_ids_md(results):
    """更新 dify/dataset_ids.md"""
    path = os.path.join(SCRIPT_DIR, "dataset_ids.md")
    lines = [
        "# Dify 知識庫 Dataset IDs\n",
        "\n",
        "| 知識庫名稱 | Dataset ID | 說明 |\n",
        "|-----------|-----------|------|\n",
    ]
    for r in results:
        lines.append(f"| {r['name']} | {r['id']} | {r['description']} |\n")
    lines += [
        "\n",
        "## 合約類型對應法條\n",
        "\n",
        "| 合約類型 | 適用知識庫 |\n",
        "|---------|----------|\n",
        "| 消費性合約（網購、訂閱） | taiwan_consumer_protection_law |\n",
        "| 租賃合約（房租） | taiwan_civil_law, taiwan_consumer_protection_law |\n",
        "| 勞動合約（雇傭） | taiwan_labor_law |\n",
        "| 公司合約（B2B） | taiwan_company_law, taiwan_civil_law |\n",
        "| 個資相關條款 | taiwan_privacy_law |\n",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"  ✅ dataset_ids.md 已更新：{path}")


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  Dify 知識庫自動初始化")
    print("=" * 55)

    # 1. 確認 Dify 服務
    try:
        requests.get(f"{DIFY_URL}", timeout=5)
    except Exception:
        print(f"❌ 無法連線 Dify：{DIFY_URL}")
        print("   請先啟動 Dify（docker compose up）後再執行。")
        sys.exit(1)
    print(f"✅ Dify 服務正常：{DIFY_URL}\n")

    # 2. 取得 API Key
    api_key = input("請輸入 Dify Dataset API Key（格式 dataset-xxx）：").strip()
    if not api_key.startswith("dataset-"):
        print("❌ API Key 格式錯誤，應以 dataset- 開頭")
        sys.exit(1)

    # 3. 驗證 API Key
    try:
        api("GET", "/datasets?page=1&limit=1", api_key)
    except Exception as e:
        print(f"❌ API Key 驗證失敗：{e}")
        sys.exit(1)
    print("✅ API Key 驗證成功\n")

    # 3.5 取得已存在的知識庫
    print("檢查現有知識庫...", end=" ")
    existing = list_all_datasets(api_key)
    print(f"找到 {len(existing)} 個\n")

    results = []

    for ds in DATASETS:
        print(f"[{DATASETS.index(ds)+1}/{len(DATASETS)}] {ds['name']}")

        # 4. 建立知識庫
        print("    建立知識庫...", end=" ")
        try:
            created = create_dataset(ds["name"], ds["description"], api_key, existing)
            dataset_id = created["id"]
            print(f"✅  ID: {dataset_id}")
        except Exception as e:
            print(f"❌ 失敗：{e}")
            continue

        # 5. 上傳檔案
        for filepath in ds["files"]:
            if not os.path.exists(filepath):
                print(f"    ⚠️  找不到檔案，跳過：{filepath}")
                continue
            fname = os.path.basename(filepath)
            print(f"    上傳 {fname}...", end=" ")
            try:
                upload_file(dataset_id, filepath, api_key)
                print("✅")
            except Exception as e:
                print(f"❌ {e}")

        # 6. 等待 embedding
        print(f"    等待 embedding 完成（最多 300 秒）...")
        done = wait_for_indexing(dataset_id, api_key)
        if done:
            print(f"    ✅ Embedding 完成")
        else:
            print(f"    ⚠️  Embedding 超時，請至 Dify UI 確認")

        results.append({
            "name": ds["name"],
            "id": dataset_id,
            "description": ds["description"],
        })
        print()

    # 7. 輸出結果
    print("=" * 55)
    print("  完成！新的 Dataset IDs：")
    print("=" * 55)
    print(f"{'知識庫名稱':<35} {'Dataset ID'}")
    print("-" * 75)
    for r in results:
        print(f"{r['name']:<35} {r['id']}")

    print()
    update_dataset_ids_md(results)

    print()
    print("⚠️  請將以上 Dataset IDs 更新到 n8n 的")
    print("   Multi Law Retrieval 節點的 DATASET_MAP 設定中。")


if __name__ == "__main__":
    main()
