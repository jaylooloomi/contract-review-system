<template>
  <div class="min-h-screen bg-gray-100">

    <!-- Navbar -->
    <div class="bg-white shadow-sm px-6 py-3 flex items-center gap-3">
      <button class="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1" @click="$router.push('/')">
        ← 返回上傳
      </button>
      <span class="text-gray-400 text-sm">|</span>
      <span class="text-gray-600 text-sm font-medium">{{ result?.filename }}</span>
    </div>

    <div v-if="!result" class="text-center text-gray-500 py-20">
      <p>找不到分析結果，請重新上傳合約</p>
      <button class="mt-4 text-blue-600 underline" @click="$router.push('/')">返回上傳</button>
    </div>

    <div v-else class="p-6 max-w-screen-xl mx-auto space-y-5">

      <!-- Dashboard Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <!-- 風險評分 -->
        <div class="bg-white rounded-2xl shadow p-5 flex flex-col items-center justify-center gap-2">
          <div
            class="w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold text-white"
            :class="scoreColor"
          >{{ analysis.riskScore }}</div>
          <p class="text-xs text-gray-500 font-medium">風險評分</p>
        </div>

        <!-- 合約類型 -->
        <div class="bg-white rounded-2xl shadow p-5 flex flex-col items-center justify-center gap-2">
          <p class="text-2xl font-bold text-gray-800">{{ analysis.contractType || '一般合約' }}</p>
          <p class="text-xs text-gray-500 font-medium">合約類型</p>
        </div>

        <!-- 適用法規 -->
        <div class="bg-white rounded-2xl shadow p-5 flex flex-col items-center justify-center gap-2">
          <div class="flex flex-wrap gap-1 justify-center">
            <span
              v-for="law in displayLaws"
              :key="law"
              class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium"
            >{{ law }}</span>
          </div>
          <p class="text-xs text-gray-500 font-medium mt-1">適用法規</p>
        </div>

        <!-- 違法條款數 -->
        <div class="bg-white rounded-2xl shadow p-5 flex flex-col items-center justify-center gap-2">
          <p class="text-4xl font-bold" :class="analysis.totalViolations > 0 ? 'text-red-500' : 'text-green-500'">
            {{ analysis.totalViolations }}
          </p>
          <p class="text-xs text-gray-500 font-medium">疑似違法條款</p>
        </div>
      </div>

      <!-- 摘要 -->
      <div class="bg-white rounded-2xl shadow px-6 py-4 text-sm text-gray-700 leading-relaxed">
        <span class="font-semibold text-gray-800 mr-2">分析摘要</span>{{ analysis.summary }}
      </div>

      <!-- 主內容：左右分割 -->
      <div class="flex gap-5 items-start">

        <!-- 左：合約原文 + 高亮 -->
        <div class="w-1/2 bg-white rounded-2xl shadow p-5">
          <h3 class="font-bold text-gray-800 mb-3 text-sm">合約原文</h3>
          <div class="text-sm leading-8 space-y-0.5">
            <template v-for="(line, i) in highlightedLines" :key="i">
              <p
                v-if="line.text.trim()"
                class="px-2 rounded transition-colors"
                :class="line.bgClass"
              >{{ line.text }}</p>
              <div v-else class="h-2"></div>
            </template>
          </div>
          <!-- 圖例 -->
          <div class="mt-4 pt-3 border-t flex gap-4 text-xs text-gray-500">
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-red-200 inline-block"></span>高風險</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-yellow-200 inline-block"></span>中風險</span>
          </div>
        </div>

        <!-- 右：違法條款卡片 -->
        <div class="w-1/2">
          <h3 class="font-bold text-gray-800 mb-3 text-sm">違法條款分析</h3>

          <div v-if="analysis.violations?.length > 0" class="space-y-4">
            <div
              v-for="v in analysis.violations"
              :key="v.id"
              class="bg-white rounded-2xl shadow p-5 border-l-4"
              :class="riskBorder(v.riskLevel)"
            >
              <!-- Badges -->
              <div class="flex flex-wrap items-center gap-2 mb-2">
                <span
                  class="text-xs font-bold px-2.5 py-0.5 rounded-full"
                  :class="riskBadge(v.riskLevel)"
                >{{ v.riskLevel }}風險</span>
                <span
                  v-if="extractLaw(v.reason)"
                  class="text-xs bg-indigo-100 text-indigo-700 px-2.5 py-0.5 rounded-full font-medium"
                >{{ extractLaw(v.reason) }}</span>
              </div>

              <!-- 條款名稱 -->
              <h4 class="font-bold text-gray-800 text-base">{{ v.clause }}</h4>

              <!-- 違法原因 -->
              <p class="text-sm text-gray-600 mt-1">{{ v.reason }}</p>

              <!-- 詳細說明 -->
              <p class="text-sm text-gray-500 mt-3 pt-3 border-t leading-relaxed">{{ v.details }}</p>
            </div>
          </div>

          <div v-else class="bg-green-50 rounded-2xl p-8 text-center text-green-700">
            <div class="text-4xl mb-3">✅</div>
            <p class="font-semibold">未偵測到明顯違法條款</p>
          </div>

          <!-- 重新分析 -->
          <div class="mt-5 text-center">
            <button
              class="px-6 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 font-semibold text-sm"
              @click="$router.push('/')"
            >分析另一份合約</button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const raw = sessionStorage.getItem('analysisResult')
const result = raw ? JSON.parse(raw) : null
const analysis = result?.analysisResult || {}

// 法規顯示名稱對照
const LAW_NAMES = {
  taiwan_consumer_protection_law: '消費者保護法',
  taiwan_civil_law: '民法',
  taiwan_labor_law: '勞動基準法',
  taiwan_privacy_law: '個資法',
  taiwan_company_law: '公司法',
}

const displayLaws = computed(() => {
  const laws = analysis.appliedLaws || []
  return laws.map(l => LAW_NAMES[l] || l)
})

// 風險評分顏色
const scoreColor = computed(() => {
  const s = analysis.riskScore || 0
  if (s >= 7) return 'bg-red-500'
  if (s >= 4) return 'bg-yellow-500'
  return 'bg-green-500'
})

// 違法條款邊框
function riskBorder(level) {
  if (level === '高') return 'border-red-500'
  if (level === '中') return 'border-yellow-400'
  return 'border-green-400'
}

// 風險 badge 顏色
function riskBadge(level) {
  if (level === '高') return 'bg-red-100 text-red-700'
  if (level === '中') return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
}

// 從 reason 萃取法規名稱
function extractLaw(reason) {
  if (!reason) return null
  if (reason.includes('民法')) return '民法'
  if (reason.includes('消保法') || reason.includes('消費者保護法')) return '消費者保護法'
  if (reason.includes('勞動基準法') || reason.includes('勞基法')) return '勞動基準法'
  if (reason.includes('個資法') || reason.includes('個人資料')) return '個資法'
  if (reason.includes('公司法')) return '公司法'
  if (reason.includes('公平交易法')) return '公平交易法'
  return null
}

// 合約原文高亮
const highlightedLines = computed(() => {
  const text = result?.originalText || ''
  if (!text) return []

  const violations = analysis.violations || []

  // 建立 keyword → riskLevel 對照表（高風險優先）
  // 移除 LLM 可能加上的「（第X條）」後綴，取得核心關鍵字
  const keywordMap = []
  for (const v of violations) {
    if (!v.clause) continue
    // 去掉括號內容，取每個詞段作為關鍵字
    const cleaned = v.clause.replace(/（[^）]*）/g, '').replace(/\([^)]*\)/g, '').trim()
    // 拆成每個詞段（至少 2 字）
    const parts = cleaned.split(/[\s　、\/]+/).filter(p => p.length >= 2)
    for (const kw of [cleaned, ...parts]) {
      if (kw) keywordMap.push({ keyword: kw, level: v.riskLevel })
    }
  }

  return text.split('\n').map(line => {
    let bgClass = ''
    for (const { keyword, level } of keywordMap) {
      if (line.includes(keyword)) {
        if (level === '高') { bgClass = 'bg-red-100'; break }
        if (level === '中' && bgClass !== 'bg-red-100') bgClass = 'bg-yellow-100'
      }
    }
    return { text: line, bgClass }
  })
})
</script>
