<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div class="max-w-3xl mx-auto">

      <!-- 頂部導覽 -->
      <div class="flex items-center gap-3 mb-6">
        <button
          class="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1"
          @click="$router.push('/')"
        >← 返回上傳</button>
        <span class="text-gray-400 text-sm">{{ result?.filename }}</span>
      </div>

      <div v-if="!result" class="text-center text-gray-500 py-20">
        <p>找不到分析結果，請重新上傳合約</p>
        <button class="mt-4 text-blue-600 underline" @click="$router.push('/')">返回上傳</button>
      </div>

      <div v-else>
        <!-- 風險評分卡 -->
        <div class="bg-white rounded-2xl shadow p-6 mb-6">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-800">分析結果</h2>
              <p class="text-gray-500 text-sm mt-1">共偵測到 {{ analysis.totalViolations }} 個疑似違法條款</p>
            </div>
            <div class="text-center">
              <div
                class="w-20 h-20 rounded-full flex items-center justify-center text-3xl font-bold text-white"
                :class="scoreColor"
              >{{ analysis.riskScore }}</div>
              <p class="text-xs text-gray-500 mt-1">風險評分</p>
            </div>
          </div>

          <!-- 摘要 -->
          <div class="mt-4 p-4 bg-gray-50 rounded-xl text-sm text-gray-700 leading-relaxed">
            {{ analysis.summary }}
          </div>
        </div>

        <!-- 違法條款列表 -->
        <div v-if="analysis.violations.length > 0">
          <h3 class="font-semibold text-gray-700 mb-3">違法條款詳細</h3>
          <div class="space-y-4">
            <div
              v-for="v in analysis.violations"
              :key="v.id"
              class="bg-white rounded-2xl shadow p-5 border-l-4"
              :class="riskBorder(v.riskLevel)"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <span
                    class="inline-block text-xs font-semibold px-2 py-0.5 rounded-full mb-2"
                    :class="riskBadge(v.riskLevel)"
                  >{{ v.riskLevel }}風險</span>
                  <h4 class="font-bold text-gray-800">{{ v.clause }}</h4>
                  <p class="text-sm text-gray-600 mt-1">{{ v.reason }}</p>
                </div>
              </div>
              <p class="text-sm text-gray-500 mt-3 leading-relaxed border-t pt-3">{{ v.details }}</p>
            </div>
          </div>
        </div>

        <div v-else class="bg-green-50 rounded-2xl p-6 text-center text-green-700">
          <div class="text-3xl mb-2">✅</div>
          <p class="font-semibold">未偵測到明顯違法條款</p>
        </div>

        <!-- 重新分析 -->
        <div class="mt-8 text-center">
          <button
            class="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 font-semibold"
            @click="$router.push('/')"
          >分析另一份合約</button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const raw = sessionStorage.getItem('analysisResult')
const result = raw ? JSON.parse(raw) : null
const analysis = result?.analysisResult || {}

const scoreColor = computed(() => {
  const s = analysis.riskScore || 0
  if (s >= 7) return 'bg-red-500'
  if (s >= 4) return 'bg-yellow-500'
  return 'bg-green-500'
})

function riskBorder(level) {
  if (level === '高') return 'border-red-500'
  if (level === '中') return 'border-yellow-500'
  return 'border-green-500'
}

function riskBadge(level) {
  if (level === '高') return 'bg-red-100 text-red-700'
  if (level === '中') return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
}
</script>
