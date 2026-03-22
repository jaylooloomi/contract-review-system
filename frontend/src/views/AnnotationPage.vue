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
        <div class="bg-white rounded-2xl shadow p-5 flex flex-col items-center justify-center gap-2">
          <div class="w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold text-white" :class="scoreColor">
            {{ analysis.riskScore }}
          </div>
          <p class="text-xs text-gray-500 font-medium">風險評分</p>
        </div>
        <div class="bg-white rounded-2xl shadow p-5 flex flex-col items-center justify-center gap-2">
          <p class="text-2xl font-bold text-gray-800">{{ analysis.contractType || '一般合約' }}</p>
          <p class="text-xs text-gray-500 font-medium">合約類型</p>
        </div>
        <div class="bg-white rounded-2xl shadow p-5 flex flex-col items-center justify-center gap-2">
          <div class="flex flex-wrap gap-1 justify-center">
            <span v-for="law in displayLaws" :key="law" class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">{{ law }}</span>
          </div>
          <p class="text-xs text-gray-500 font-medium mt-1">適用法規</p>
        </div>
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

        <!-- 左：PDF 原文 iframe -->
        <div class="w-1/2 bg-white rounded-2xl shadow p-5 sticky top-6">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-bold text-gray-800 text-sm">合約原文</h3>
            <div class="flex gap-3 text-xs text-gray-400">
              <span class="flex items-center gap-1"><span class="w-3 h-3 rounded inline-block highlight-high-demo"></span>高風險</span>
              <span class="flex items-center gap-1"><span class="w-3 h-3 rounded inline-block highlight-mid-demo"></span>中風險</span>
            </div>
          </div>
          <iframe
            v-if="pdfHtml"
            ref="pdfIframe"
            class="w-full rounded-lg border border-gray-100"
            style="height: 65vh;"
            @load="onIframeLoad"
          ></iframe>
          <div v-else class="text-center text-gray-400 py-10 text-sm">無法載入合約原文</div>
        </div>

        <!-- 右：違法條款卡片 -->
        <div class="w-1/2">
          <h3 class="font-bold text-gray-800 mb-3 text-sm">違法條款分析
            <span class="text-gray-400 font-normal text-xs ml-2">點擊條款可定位原文</span>
          </h3>

          <div v-if="analysis.violations?.length > 0" class="space-y-4">
            <div
              v-for="v in analysis.violations"
              :key="v.id"
              class="bg-white rounded-2xl shadow p-5 border-l-4 cursor-pointer transition-all duration-200"
              :class="[
                riskBorder(v.riskLevel),
                activeViolationId === v.id ? 'ring-2 ring-blue-400 shadow-lg' : 'hover:shadow-md'
              ]"
              @click="scrollToViolation(v)"
            >
              <div class="flex flex-wrap items-center gap-2 mb-2">
                <span class="text-xs font-bold px-2.5 py-0.5 rounded-full" :class="riskBadge(v.riskLevel)">{{ v.riskLevel }}風險</span>
                <span v-if="extractLaw(v.reason, v.details)" class="text-xs bg-indigo-100 text-indigo-700 px-2.5 py-0.5 rounded-full font-medium">{{ extractLaw(v.reason, v.details) }}</span>
              </div>
              <h4 class="font-bold text-gray-800 text-base">{{ v.clause }}</h4>
              <p class="text-sm text-gray-600 mt-1">{{ v.reason }}</p>
              <p class="text-sm text-gray-500 mt-3 pt-3 border-t leading-relaxed">{{ v.details }}</p>
            </div>
          </div>

          <div v-else class="bg-green-50 rounded-2xl p-8 text-center text-green-700">
            <div class="text-4xl mb-3">✅</div>
            <p class="font-semibold">未偵測到明顯違法條款</p>
          </div>

          <div class="mt-5 text-center">
            <button class="px-6 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 font-semibold text-sm" @click="$router.push('/')">
              分析另一份合約
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, nextTick } from 'vue'

const raw = sessionStorage.getItem('analysisResult')
const result = raw ? JSON.parse(raw) : null
const analysis = result?.analysisResult || {}
const pdfHtml = sessionStorage.getItem('pdfHtml') || ''

const pdfIframe = ref(null)
const activeViolationId = ref(null)
const iframeReady = ref(false)

const LAW_NAMES = {
  taiwan_consumer_protection_law: '消費者保護法',
  taiwan_civil_law: '民法',
  taiwan_labor_law: '勞動基準法',
  taiwan_privacy_law: '個資法',
  taiwan_company_law: '公司法',
}

const displayLaws = computed(() => {
  const lawSet = new Set()
  const laws = analysis.appliedLaws || []
  laws.forEach(l => lawSet.add(LAW_NAMES[l] || l))
  const violations = analysis.violations || []
  violations.forEach(v => {
    const law = extractLaw(v.reason, v.details)
    if (law) lawSet.add(law)
  })
  return [...lawSet]
})

const scoreColor = computed(() => {
  const s = analysis.riskScore || 0
  if (s >= 7) return 'bg-red-500'
  if (s >= 4) return 'bg-yellow-500'
  return 'bg-green-500'
})

function riskBorder(level) {
  if (level === '高') return 'border-red-500'
  if (level === '中') return 'border-yellow-400'
  return 'border-green-400'
}

function riskBadge(level) {
  if (level === '高') return 'bg-red-100 text-red-700'
  if (level === '中') return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
}

function extractLaw(reason, details) {
  const text = (reason || '') + ' ' + (details || '')
  if (text.includes('民法')) return '民法'
  if (text.includes('消保法') || text.includes('消費者保護法')) return '消費者保護法'
  if (text.includes('勞動基準法') || text.includes('勞基法')) return '勞動基準法'
  if (text.includes('個資法') || text.includes('個人資料保護')) return '個資法'
  if (text.includes('公司法')) return '公司法'
  if (text.includes('公平交易法')) return '公平交易法'
  if (text.includes('營業秘密法') || text.includes('營業秘密')) return '營業秘密法'
  if (text.includes('著作權法') || text.includes('著作權')) return '著作權法'
  if (text.includes('專利法')) return '專利法'
  if (text.includes('仲裁法')) return '仲裁法'
  if (text.includes('保險法')) return '保險法'
  if (text.includes('定型化契約') || text.includes('消費者') || text.includes('預付')) return '消費者保護法'
  if (text.includes('勞工') || text.includes('工資') || text.includes('工時')) return '勞動基準法'
  return null
}

function getKeywords(v) {
  const keywords = []
  const quotePattern = /[「『""]([^」』""]{2,})[」』""]/g
  for (const field of [v.reason, v.details]) {
    if (!field) continue
    let m
    while ((m = quotePattern.exec(field)) !== null) {
      const fragments = m[1].split(/\.{2,}|…|；|。/).map(s => s.trim()).filter(s => s.length >= 3)
      keywords.push(...fragments)
    }
  }
  if (v.clause) {
    const cleaned = v.clause.replace(/（[^）]*）/g, '').replace(/\([^)]*\)/g, '').trim()
    const parts = cleaned.split(/[\s　、\/之的及與或等]+/).filter(p => p.length >= 2)
    keywords.push(cleaned, ...parts)
  }
  return [...new Set(keywords.filter(Boolean))]
}

// iframe 載入後寫入 HTML
function onIframeLoad() {
  const iframe = pdfIframe.value
  if (!iframe) return
  const doc = iframe.contentDocument || iframe.contentWindow?.document
  if (!doc) return
  doc.open()
  doc.write(pdfHtml)
  doc.close()
  iframeReady.value = true
}

// 點擊卡片：在 iframe 內高亮並捲動
function scrollToViolation(v) {
  activeViolationId.value = v.id
  const iframe = pdfIframe.value
  if (!iframe) return
  const doc = iframe.contentDocument || iframe.contentWindow?.document
  if (!doc) return

  const keywords = getKeywords(v)
  const cls = v.riskLevel === '高' ? 'highlight-high' : 'highlight-mid'

  // 清除上一次高亮
  doc.querySelectorAll('.pdf-block.highlight-high, .pdf-block.highlight-mid, .pdf-block.highlight-active').forEach(el => {
    el.classList.remove('highlight-high', 'highlight-mid', 'highlight-active')
  })

  // 找符合關鍵字的 block 並高亮
  let firstMatch = null
  doc.querySelectorAll('.pdf-block').forEach(block => {
    const text = block.textContent || ''
    if (keywords.some(kw => text.includes(kw))) {
      block.classList.add(cls, 'highlight-active')
      if (!firstMatch) firstMatch = block
    }
  })

  if (firstMatch) firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

// 設定 iframe srcdoc（Vue 掛載後）
import { onMounted } from 'vue'
onMounted(() => {
  nextTick(() => {
    const iframe = pdfIframe.value
    if (!iframe || !pdfHtml) return
    // 用 srcdoc 觸發 load 事件
    iframe.srcdoc = '<!DOCTYPE html><html><body></body></html>'
  })
})
</script>

<style scoped>
.highlight-high-demo { background-color: rgba(252,165,165,0.55); border: 1px solid #fca5a5; }
.highlight-mid-demo { background-color: rgba(253,224,71,0.55); border: 1px solid #fde047; }
</style>
