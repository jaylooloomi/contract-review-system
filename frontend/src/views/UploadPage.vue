<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-lg p-8 w-full max-w-lg">

      <!-- 標題 -->
      <h1 class="text-2xl font-bold text-gray-800 mb-2">合約審閱系統</h1>
      <p class="text-gray-500 text-sm mb-8">上傳 PDF 合約，自動偵測違反台灣消保法的條款</p>

      <!-- 上傳區域 -->
      <div
        class="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors"
        :class="dragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'"
        @dragover.prevent="dragging = true"
        @dragleave="dragging = false"
        @drop.prevent="onDrop"
        @click="$refs.fileInput.click()"
      >
        <div v-if="!selectedFile">
          <div class="text-4xl mb-3">📄</div>
          <p class="text-gray-600 font-medium">點擊或拖曳 PDF 檔案到此處</p>
          <p class="text-gray-400 text-sm mt-1">僅支援 .pdf 格式，最大 20MB</p>
        </div>
        <div v-else class="text-left">
          <div class="flex items-center gap-3">
            <span class="text-2xl">📋</span>
            <div>
              <p class="font-medium text-gray-800">{{ selectedFile.name }}</p>
              <p class="text-sm text-gray-400">{{ (selectedFile.size / 1024).toFixed(1) }} KB</p>
            </div>
            <button
              class="ml-auto text-gray-400 hover:text-red-500 text-xl"
              @click.stop="clearFile"
            >✕</button>
          </div>
        </div>
      </div>

      <input ref="fileInput" type="file" accept=".pdf" class="hidden" @change="onFileChange" />

      <!-- 錯誤訊息 -->
      <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
        {{ error }}
      </div>

      <!-- 上傳按鈕 -->
      <button
        class="mt-6 w-full py-3 rounded-xl font-semibold text-white transition-all"
        :class="canUpload ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-300 cursor-not-allowed'"
        :disabled="!canUpload || loading"
        @click="upload"
      >
        <span v-if="loading" class="flex items-center justify-center gap-2">
          <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
          </svg>
          分析中，請稍候...
        </span>
        <span v-else>開始分析</span>
      </button>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const fileInput = ref(null)
const selectedFile = ref(null)
const loading = ref(false)
const error = ref('')
const dragging = ref(false)

const canUpload = computed(() => selectedFile.value && !loading.value)

function onFileChange(e) {
  const file = e.target.files[0]
  if (file) setFile(file)
}

function onDrop(e) {
  dragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) setFile(file)
}

function setFile(file) {
  error.value = ''
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    error.value = '請上傳 PDF 格式的檔案'
    return
  }
  if (file.size > 20 * 1024 * 1024) {
    error.value = '檔案大小超過 20MB 限制'
    return
  }
  selectedFile.value = file
}

function clearFile() {
  selectedFile.value = null
  error.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

async function upload() {
  if (!canUpload.value) return
  loading.value = true
  error.value = ''

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const res = await axios.post('http://127.0.0.1:8000/api/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    })
    sessionStorage.setItem('analysisResult', JSON.stringify(res.data))
    router.push('/annotation')
  } catch (e) {
    error.value = e.response?.data?.detail || '分析失敗，請確認後端服務是否正常運行'
  } finally {
    loading.value = false
  }
}
</script>
