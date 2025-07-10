<template>
  <div class="report-result-simple-bg">
    <el-row justify="center">
      <el-col :xs="24" :sm="22" :md="22" :lg="20" :xl="18" style="max-width: 1100px;">
        <el-card class="result-card">
          <div class="markdown-body" v-html="renderMarkdown(reportRaw)"></div>
        </el-card>
        <div class="result-footer">
          <el-button type="primary" @click="goBack" style="margin-top: 32px;">
            返回
          </el-button>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
const route = useRoute()
const router = useRouter()
const reportRaw = route.query.report || '无内容'

function renderMarkdown(content) {
  if (!content) return ''
  let html = marked(content)
  // 可根据需要添加自定义处理
  return DOMPurify.sanitize(html)
}

function goBack() {
  router.push('/report')
}
</script>

<style>
.report-result-simple-bg {
  min-height: 100vh;
  background: #fff;
  position: relative;
  overflow-x: hidden;
}
.simple-header {
  width: 100%;
  padding: 40px 0 16px 0;
  background: #fff;
  text-align: center;
  margin-bottom: 24px;
}
.main-title {
  font-size: 2.1rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 6px;
  letter-spacing: 1px;
}
.subtitle {
  color: #888;
  font-size: 1.05em;
  margin-bottom: 0;
}
.result-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(64,158,255,0.08);
  background: #fff;
  margin-bottom: 32px;
  padding: 32px 24px 24px 24px;
  font-size: 1.08em;
  white-space: pre-wrap;
  min-height: 200px;
}
.result-card h1 {
  font-size: 2.1em;
  font-weight: bold;
  margin: 1.1em 0 0.7em 0;
  color: #222;
}
.result-card h2 {
  font-size: 1.5em;
  font-weight: bold;
  margin: 1em 0 0.6em 0;
  color: #333;
}
.result-card h3 {
  font-size: 1.2em;
  font-weight: bold;
  margin: 0.9em 0 0.5em 0;
  color: #444;
}
.result-footer {
  text-align: center;
}
</style> 