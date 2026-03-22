<template>
  <div class="h-screen flex flex-col bg-gray-100 overflow-hidden">

    <!-- Navbar -->
    <div class="bg-white shadow-sm shrink-0">
      <div class="py-3 px-6 flex items-center gap-3">
        <button class="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1" @click="$router.push('/')">
          ← 返回上傳
        </button>
        <span class="text-gray-400 text-sm">|</span>
        <span class="text-gray-600 text-sm font-medium truncate">{{ result?.filename }}</span>
      </div>
    </div>

    <div v-if="!result" class="text-center text-gray-500 py-20">
      <p>找不到分析結果，請重新上傳合約</p>
      <button class="mt-4 text-blue-600 underline" @click="$router.push('/')">返回上傳</button>
    </div>

    <div v-else class="flex flex-col flex-1 overflow-hidden">

      <!-- Dashboard 4 卡片 -->
      <div class="flex justify-center px-6 py-3 shrink-0">
        <div class="flex gap-3 w-full max-w-3xl">
          <!-- 風險評分 -->
          <div class="flex-1 bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
            <p class="text-xs text-gray-400 mb-1">風險評分</p>
            <p class="text-2xl font-bold" :class="scoreColor">{{ analysis.riskScore ?? '-' }}<span class="text-sm font-normal text-gray-400">/10</span></p>
          </div>
          <!-- 合約類型 -->
          <div class="flex-1 bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
            <p class="text-xs text-gray-400 mb-1">合約類型</p>
            <p class="text-base font-bold text-gray-800 leading-tight">{{ analysis.contractType || '一般合約' }}</p>
          </div>
          <!-- 適用法規 -->
          <div class="flex-1 bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
            <p class="text-xs text-gray-400 mb-1">適用法規</p>
            <p class="text-base font-bold text-gray-800 leading-tight">
              {{ displayLaws.length > 0 ? displayLaws.join(' + ') : '—' }}
            </p>
          </div>
          <!-- 違法條款 -->
          <div class="flex-1 bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
            <p class="text-xs text-gray-400 mb-1">違法條款</p>
            <p class="text-2xl font-bold" :class="analysis.totalViolations > 0 ? 'text-red-500' : 'text-green-500'">
              {{ analysis.totalViolations ?? 0 }}<span class="text-sm font-normal text-gray-400"> 條</span>
            </p>
          </div>
        </div>
      </div>

      <!-- 摘要 -->
      <div class="flex justify-center px-6 shrink-0 pb-2">
        <div class="bg-white/80 rounded-xl px-5 py-2 text-xs text-gray-600 leading-relaxed shadow-sm w-full max-w-3xl">
          <span class="font-semibold text-gray-700 mr-2">分析摘要</span>{{ analysis.summary }}
        </div>
      </div>

      <!-- PDF 全寬區域 -->
      <div class="flex-1 relative overflow-hidden">

        <!-- PDF iframe -->
        <iframe
          v-if="pdfHtml"
          ref="pdfIframe"
          class="w-full h-full border-0"
          @load="onIframeLoad"
        ></iframe>
        <div v-else class="flex items-center justify-center h-full text-gray-400 text-sm bg-white">
          無法載入合約原文
        </div>

        <!-- 右側滑出抽屜面板 -->
        <div
          class="fixed top-0 bottom-0 right-0 flex flex-row z-20"
          :style="panelStyle"
        >
          <!-- Tab 收合按鈕 -->
          <div
            class="w-10 shrink-0 flex flex-col items-center justify-center gap-2 cursor-pointer bg-white/90 backdrop-blur-sm border-l border-t border-b border-gray-200 rounded-l-2xl shadow-lg py-6 select-none"
            @click="isOpen = !isOpen"
          >
            <span class="text-base">⚠️</span>
            <span class="text-gray-600 text-xs font-bold leading-none" style="writing-mode: vertical-rl; letter-spacing: 0.2em">違法條款</span>
            <span class="text-gray-400 text-xs mt-1">{{ isOpen ? '›' : '‹' }}</span>
          </div>

          <!-- 面板內容 -->
          <div class="flex flex-col w-[340px] bg-white/95 backdrop-blur-sm rounded-tr-2xl rounded-br-2xl shadow-2xl border border-gray-100 overflow-hidden">
            <!-- 面板標題 -->
            <div class="px-4 py-3 border-b border-gray-100 shrink-0">
              <div class="flex items-center justify-between">
                <h3 class="font-bold text-gray-800 text-sm">違法條款分析</h3>
                <span class="text-gray-400 font-normal text-xs">點擊定位原文</span>
              </div>
              <div class="flex gap-3 text-xs text-gray-400 mt-1.5">
                <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm inline-block highlight-high-demo"></span>高風險</span>
                <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm inline-block highlight-mid-demo"></span>中風險</span>
              </div>
            </div>

            <!-- 卡片列表 -->
            <div class="flex-1 overflow-y-auto px-3 py-3 space-y-2.5">
              <div
                v-for="v in analysis.violations"
                :key="v.id"
                class="rounded-xl border border-gray-100 shadow-sm p-3.5 border-l-4 cursor-pointer transition-all duration-200"
                :class="[
                  riskBorder(v.riskLevel),
                  activeViolationId === v.id ? 'ring-2 ring-blue-400 shadow-md bg-blue-50/30' : 'hover:shadow-md bg-white'
                ]"
                @click="scrollToViolation(v)"
              >
                <div class="flex flex-wrap items-center gap-1.5 mb-1.5">
                  <span class="text-xs font-bold px-2 py-0.5 rounded-full" :class="riskBadge(v.riskLevel)">{{ v.riskLevel }}風險</span>
                  <span v-if="extractLaw(v.reason, v.details)" class="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full font-medium">{{ extractLaw(v.reason, v.details) }}</span>
                </div>
                <h4 class="font-bold text-gray-800 text-sm leading-tight">{{ v.clause }}</h4>
                <p class="text-xs text-gray-500 mt-1.5 leading-relaxed">{{ v.details }}</p>
              </div>

              <div v-if="!(analysis.violations?.length > 0)" class="bg-green-50 rounded-xl p-6 text-center text-green-700">
                <div class="text-2xl mb-1">✅</div>
                <p class="font-semibold text-sm">未偵測到明顯違法條款</p>
              </div>
            </div>

            <!-- 底部按鈕 -->
            <div class="px-3 py-3 border-t border-gray-100 shrink-0">
              <button class="w-full py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 font-semibold text-xs" @click="$router.push('/')">
                分析另一份合約
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, nextTick, onMounted } from 'vue'

const raw = sessionStorage.getItem('analysisResult')
const result = raw ? JSON.parse(raw) : null
const analysis = result?.analysisResult || {}
const pdfHtml = sessionStorage.getItem('pdfHtml') || ''

const pdfIframe = ref(null)
const activeViolationId = ref(null)
const iframeReady = ref(false)

// 抽屜開關：桌機預設展開，手機預設收合
const isOpen = ref(typeof window !== 'undefined' ? window.innerWidth >= 768 : true)

// 面板滑入/滑出動畫：收合時只露出 40px tab
const panelStyle = computed(() => ({
  transform: isOpen.value ? 'translateX(0)' : 'translateX(340px)',
  transition: 'transform 0.3s ease',
}))

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
  if (s >= 7) return 'text-red-500'
  if (s >= 4) return 'text-yellow-500'
  return 'text-green-500'
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

function onIframeLoad() {
  iframeReady.value = true
}

function scrollToViolation(v) {
  activeViolationId.value = v.id
  const iframe = pdfIframe.value
  if (!iframe) return
  const doc = iframe.contentDocument || iframe.contentWindow?.document
  if (!doc) return

  const keywords = getKeywords(v)
  const cls = v.riskLevel === '高' ? 'highlight-high' : 'highlight-mid'

  doc.querySelectorAll('.t.highlight-high, .t.highlight-mid, .t.highlight-active').forEach(el => {
    el.classList.remove('highlight-high', 'highlight-mid', 'highlight-active')
  })

  let firstMatch = null
  doc.querySelectorAll('.t').forEach(el => {
    const text = el.textContent || ''
    if (keywords.some(kw => text.includes(kw))) {
      el.classList.add(cls, 'highlight-active')
      if (!firstMatch) firstMatch = el
    }
  })

  if (firstMatch) {
    const container = doc.getElementById('page-container')
    if (container) {
      const elRect = firstMatch.getBoundingClientRect()
      const containerRect = container.getBoundingClientRect()
      container.scrollTop += elRect.top - containerRect.top - container.clientHeight / 2
    } else {
      firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }
}

onMounted(() => {
  nextTick(() => {
    const iframe = pdfIframe.value
    if (!iframe || !pdfHtml) return
    iframe.srcdoc = pdfHtml
  })
})
</script>

<style scoped>
.highlight-high-demo { background-color: rgba(252,165,165,0.7); border: 1px solid #fca5a5; }
.highlight-mid-demo { background-color: rgba(253,224,71,0.7); border: 1px solid #fde047; }
</style>
