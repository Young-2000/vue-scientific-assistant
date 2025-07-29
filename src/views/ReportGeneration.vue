<template>
  <div class="report-generation-simple-bg">
    <div class="simple-header">
      <h2 class="main-title">报告生成</h2>
      <div class="subtitle">一键生成专业报告，支持自定义模板</div>
    </div>
    <el-row justify="center">
      <el-col :xs="24" :sm="22" :md="22" :lg="20" :xl="18" style="max-width: 1100px;">
        <el-card class="gen-card">
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            @submit.prevent="handleSubmit"
            class="form-section"
            label-width="100px"
            label-position="top"
          >
            <el-form-item label="指令 instruction">
              <el-input v-model="form.instruction" clearable />
              <template #description>
                <div class="form-tip">指令为可选项，可用于指定报告风格、语言等。</div>
              </template>
            </el-form-item>
            <el-form-item label="主题 topic" prop="topic" required>
              <el-input v-model="form.topic" clearable />
              <template #description>
                <div class="form-tip">主题为必填项，请输入报告的主题。</div>
              </template>
            </el-form-item>
            <el-form-item label="模板 template" prop="template" required>
              <el-upload
                class="upload-demo"
                :show-file-list="false"
                :auto-upload="false"
                :before-upload="() => false"
                accept=".txt,.docx"
                @change="handleFileChange"
              >
                <el-button type="primary">
                  <el-icon><UploadFilled /></el-icon>
                  选择文件
                </el-button>
                <span v-if="fileName" class="file-name"><el-icon><Document /></el-icon> 已上传: {{ fileName }}</span>
              </el-upload>
              <template #description>
                <div class="form-tip">模板为必填项，仅支持 txt 或 docx 文件。</div>
              </template>
            </el-form-item>
            
            <!-- 添加知识库选择 -->
            <el-form-item label="选择知识库" class="kb-selection">
              <div v-if="kbLoading" class="kb-loading">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>正在加载知识库列表...</span>
              </div>
              <div v-else-if="kbError" class="kb-error">
                <el-icon><WarningFilled /></el-icon>
                <span>{{ kbError }}</span>
                <el-button type="primary" link @click="loadKnowledgeBases">重试</el-button>
              </div>
              <div v-else-if="knowledgeBases.length === 0" class="kb-empty">
                <el-icon><InfoFilled /></el-icon>
                <span>暂无可用知识库</span>
              </div>
              <el-radio-group v-else v-model="selectedKbId" class="kb-radio-group">
                <el-radio 
                  v-for="kb in knowledgeBases" 
                  :key="kb.id" 
                  :label="kb.id" 
                  border
                  class="kb-radio-item"
                >
                  {{ kb.name }}
                </el-radio>
              </el-radio-group>
              <template #description>
                <div class="form-tip">选择要用于生成报告的知识库（可选）。</div>
              </template>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%;">
                <el-icon><MagicStick /></el-icon>
                生成报告
              </el-button>
            </el-form-item>
          </el-form>
          <div v-if="loading" class="loading-section">
            <div class="loading-card">
              <div class="loading-content">
                <div class="loading-spinner">
                  <div class="spinner-ring"></div>
                  <div class="spinner-ring"></div>
                  <div class="spinner-ring"></div>
                </div>
                <h3>正在生成报告</h3>
                <p>AI正在为您分析内容并生成专业报告...</p>
                <el-progress :percentage="progress" class="mb-2" style="margin: 24px 0 0 0;" v-if="progress > 0 && progress < 100" />
                <div class="loading-dots">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>
          <el-alert v-if="error" :title="error" type="error" show-icon class="mt-2" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import mammoth from 'mammoth'
import { useRouter } from 'vue-router'
import { 
  Document, 
  UploadFilled, 
  MagicStick, 
  Loading, 
  WarningFilled, 
  InfoFilled 
} from '@element-plus/icons-vue'

const form = ref({
  instruction: '',
  topic: '',
  template: ''
})
const fileName = ref('')
const authToken = ref('')

const loading = ref(false)
const error = ref('')
const progress = ref(0)
const formRef = ref()

// 知识库相关
const knowledgeBases = ref([])
const selectedKbId = ref('')
const kbLoading = ref(false)
const kbError = ref('')

const rules = {
  topic: [
    { required: true, message: '请输入报告主题', trigger: 'blur' }
  ],
  template: [
    { required: true, message: '请上传模板文件', trigger: 'change' }
  ]
}

const router = useRouter()

async function login() {
  const loginData = {
    email: '123@123.com',
    password: 'hXWqKtPnAt+tvQeaKHh87nNc5xbuVJu5thZtH1gBOzFfwmjml8DJp3/E2HzILWJVqWy3Vp79g3wPC67+ImkG1IQyvD4BSYXp4zlUy++toYQO1GOEMys4Xn8Xta2G9KTkjhWrR9qfOyEroIIzXEy2+HBf4DenGXPABLIh0HAGlZSdizpq3mHbIhHm26CDl0OIT7S7xd6YCOYpM9VC6IMYQI/a3r5qZc8cIvkQGrEnrhlPVIPQocxY5shmXwaEJxugPd/kezvsienh6TEfctqVcSwIssIgPBunOVJb2PDCF/NevwS3ZGqmFn7VIxUwHi0oz4KYZsudj+K8aJqG/8Jj8w=='
  };
  const resp = await fetch('http://127.0.0.1/v1/user/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(loginData)
  });
  if (!resp.ok) throw new Error('登录失败');
  let token = resp.headers.get('Authorization');
  if (!token) {
    const body = await resp.json();
    token = body.data?.access_token;
  }
  if (!token) throw new Error('未获取到token');
  authToken.value = token;
  return token;
}

// 加载知识库列表
async function loadKnowledgeBases() {
  kbLoading.value = true;
  kbError.value = '';
  
  try {
    // 确保已登录
    const token = authToken.value || await login();
    
    // 获取知识库列表
    const response = await fetch('http://127.0.0.1/v1/kb/list', {
      method: 'GET',
      headers: {
        'Authorization': token,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('获取知识库列表失败');
    }
    
    const data = await response.json();
    console.log('知识库列表返回数据:', data);
    
    if (data.code === 0 && data.data && data.data.kbs) {
      knowledgeBases.value = data.data.kbs.map(kb => ({
        id: kb.id,
        name: kb.name || `知识库 ${kb.id}`
      }));
      console.log('处理后的知识库列表:', knowledgeBases.value);
    } else {
      knowledgeBases.value = [];
      console.log('未找到知识库或返回格式不正确');
    }
  } catch (err) {
    console.error('加载知识库失败:', err);
    kbError.value = err.message || '加载知识库失败';
  } finally {
    kbLoading.value = false;
  }
}

async function handleFileChange(fileEvent) {
  let file = fileEvent.raw || fileEvent.target?.files?.[0] || fileEvent;
  if (!file) return;
  fileName.value = file.name;
  if (file.type === 'text/plain') {
    const reader = new FileReader();
    reader.onload = (e) => {
      form.value.template = e.target.result;
    };
    reader.readAsText(file);
  } else if (
    file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ) {
    const arrayBuffer = await file.arrayBuffer();
    const { value } = await mammoth.extractRawText({ arrayBuffer });
    form.value.template = value;
  } else {
    form.value.template = '';
    fileName.value = '';
    alert('仅支持 txt 或 docx 文件');
  }
}

async function handleSubmit() {
  formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    error.value = ''
    progress.value = 0
    try {
      await login();
      // 1. 第一次set，空DSL，获取id和title
      const emptySetPayload = {
        title: `test_${Math.random().toString(36).slice(2, 10)}`,
        dsl: {
          graph: {
            nodes: [
              {
                id: 'begin',
                type: 'beginNode',
                position: { x: 50, y: 200 },
                data: { label: 'Begin', name: 'begin' },
                sourcePosition: 'left',
                targetPosition: 'right'
              }
            ],
            edges: []
          },
          components: {
            begin: {
              obj: { component_name: 'Begin', params: {} },
              downstream: [],
              upstream: []
            }
          },
          messages: [],
          reference: [],
          history: [],
          path: [],
          answer: []
        }
      }
      const setResp1 = await fetch('http://127.0.0.1/v1/canvas/set', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authToken.value
        },
        body: JSON.stringify(emptySetPayload)
      })
      if (!setResp1.ok) throw new Error('首次set接口失败')
      const setJson1 = await setResp1.json()
      const unique_id = setJson1.data?.id
      const set_title = setJson1.data?.title
      if (!unique_id || !set_title) throw new Error('首次set未返回id或title')

      // 2. 用public/dsl.json内容，带id和title再次set
      const dslResp = await fetch('/dsl.json')
      if (!dslResp.ok) throw new Error('dsl.json 读取失败')
      const dslData = await dslResp.json()
      dslData.id = unique_id
      dslData.title = set_title
      const setResp2 = await fetch('http://127.0.0.1/v1/canvas/set', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authToken.value
        },
        body: JSON.stringify(dslData)
      })
      if (!setResp2.ok) throw new Error('第二次set接口失败')

      // 3. 替换query和graph.nodes中相关字段后，再set
      // 替换 components.begin.obj.params.query
      const queryList = dslData.dsl?.components?.begin?.obj?.params?.query || []
      for (const q of queryList) {
        if (q.key === 'instruction') q.value = form.value.instruction
        if (q.key === 'topic') q.value = form.value.topic
        if (q.key === 'template') q.value = form.value.template
      }
      
      // 替换 graph.nodes 里的 form.query
      const nodes = dslData.dsl?.graph?.nodes || []
      for (const node of nodes) {
        const formObj = node.data?.form
        if (formObj && Array.isArray(formObj.query)) {
          for (const q of formObj.query) {
            if (q.key === 'instruction') q.value = form.value.instruction
            if (q.key === 'topic') q.value = form.value.topic
            if (q.key === 'template') q.value = form.value.template
          }
        }
        
        // 添加选中的知识库ID到kb_ids字段
        if (formObj && formObj.kb_ids !== undefined && selectedKbId.value) {
          formObj.kb_ids = [selectedKbId.value];
          console.log(`已将知识库ID ${selectedKbId.value} 添加到节点 ${node.id}`);
        }
      }
      
      const setResp3 = await fetch('http://127.0.0.1/v1/canvas/set', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authToken.value
        },
        body: JSON.stringify(dslData)
      })
      if (!setResp3.ok) throw new Error('第三次set接口失败')

      // 4. reset
      const resetResp = await fetch('http://127.0.0.1/v1/canvas/reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authToken.value
        },
        body: JSON.stringify({ id: unique_id })
      })
      if (!resetResp.ok) throw new Error('reset接口失败')

      // 5. completion - 重新获取token
      const freshToken = await login();
      const completionResp = await fetch('http://127.0.0.1/v1/canvas/completion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': freshToken
        },
        body: JSON.stringify({ id: unique_id })
      })
      if (!completionResp.ok) throw new Error('completion接口失败')
      // 读取 completion 流式响应
      const reader = completionResp.body.getReader()
      const decoder = new TextDecoder()
      let done = false
      let chunkCount = 0
      const maxChunks = 20
      let answer = ''
      let buffer = '' // 新增缓存
      while (!done) {
        const { value, done: readerDone } = await reader.read()
        done = readerDone
        if (value) {
          chunkCount++
          progress.value = Math.min(99, Math.floor((chunkCount / maxChunks) * 100))
        }
        const text = decoder.decode(value, { stream: true })
        buffer += text // 累加到缓存
        // 按行分割
        let lines = buffer.split('\n')
        // 最后一行可能是不完整的，留到下次
        buffer = lines.pop() // 取出最后一行，留作下次拼接
        for (const line of lines) {
          if (line.startsWith('data:')) {
            const dataStr = line.substring(5).trim()
            if (dataStr === '[DONE]' || !dataStr) continue
            try {
              const data = JSON.parse(dataStr)
              
              // 检查是否有错误
              if (data.code && data.code !== 0) {
                console.error('ReportGeneration completion 流式响应中的错误:', data);
                throw new Error(data.message || '请求失败');
              }
              
              if (data.data) {
                if (data.data.answer) {
                  answer = data.data.answer
                  console.log('answer:', answer)
                }
              }
            } catch (e) {
              // 检查原始数据中是否包含错误信息
              if (dataStr.includes('"code":401') || dataStr.includes('Unauthorized')) {
                throw new Error('认证失败，请重新登录');
              } else if (dataStr.includes('"code":500') || dataStr.includes('Internal Server Error')) {
                throw new Error('服务器内部错误');
              } else if (dataStr.includes('"code":404') || dataStr.includes('Not Found')) {
                throw new Error('请求的资源不存在');
              }
              
              console.log('JSON parse error:', e, dataStr)
              answer = "生成失败，请重试"
              // 解析失败，可能是数据还没收全，留到下次
              buffer = line + '\n' + buffer // 把这行加回缓存，下次再试
              break // 跳出本轮，等下次数据
            }
          }
        }
      }
      progress.value = 100
      setTimeout(() => { progress.value = 0 }, 500)
      router.push({ path: '/report-result', query: { report: answer } })
    } catch (e) {
      error.value = e?.message || '请求失败'
    } finally {
      loading.value = false
    }
  })
}

// 组件挂载时加载知识库列表
onMounted(async () => {
  try {
    await loadKnowledgeBases();
  } catch (err) {
    console.error('初始化知识库列表失败:', err);
  }
});
</script>

<style>
.report-generation-simple-bg {
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
.gen-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(64,158,255,0.08);
  background: #fff;
  margin-bottom: 32px;
  padding: 0 0 24px 0;
  transition: box-shadow 0.2s;
}
.gen-card:hover {
  box-shadow: 0 6px 24px rgba(64,158,255,0.13);
}
.form-section {
  margin-bottom: 0;
  padding: 24px 24px 0 24px;
}
.el-form-item__content {
  padding-left: 0 !important;
}
.file-name {
  margin-left: 12px;
  color: #409EFF;
  font-size: 0.98em;
  vertical-align: middle;
}
.result-card {
  margin-top: 32px;
  background: #f6f8fa;
  padding: 1.5em;
  border-radius: 12px;
  white-space: pre-wrap;
  font-size: 1.08em;
  animation: fadeInUp 0.6s;
  box-shadow: 0 2px 12px rgba(64,158,255,0.08);
}
.result-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2em;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}
.result-icon {
  font-size: 1.4em;
}
.result-title {
  font-weight: 600;
}
.result-divider {
  margin: 8px 0 18px 0;
}
.mt-2 {
  margin-top: 16px;
}
.mt-3 {
  margin-top: 24px;
}
.fade-slide-enter-active {
  animation: fadeInUp 0.6s;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(40px); }
  to { opacity: 1; transform: translateY(0); }
}
.form-tip {
  color: #888;
  font-size: 0.98em;
  margin-top: 2px;
}
.gen-card .el-input__inner {
  padding-left: 8px !important;
}
.loading-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 500px;
}
.loading-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 60px 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(13, 110, 253, 0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}
.loading-content h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #212529;
  margin: 0 0 12px 0;
}
.loading-content p {
  color: #6c757d;
  margin: 0 0 24px 0;
}
.loading-spinner {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
}
.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top: 3px solid #0d6efd;
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
}
.spinner-ring:nth-child(2) {
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
  border-top-color: #0a58ca;
  animation-delay: 0.5s;
}
.spinner-ring:nth-child(3) {
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
  border-top-color: #084298;
  animation-delay: 1s;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.loading-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
}
.loading-dots span {
  width: 8px;
  height: 8px;
  background: #0d6efd;
  border-radius: 50%;
  animation: dots 1.4s ease-in-out infinite both;
}
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes dots {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 知识库选择样式 */
.kb-selection {
  margin-bottom: 20px;
}

.kb-loading, .kb-error, .kb-empty {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  background-color: #f8f9fa;
  color: #6c757d;
}

.kb-error {
  color: #dc3545;
  background-color: #f8d7da;
}

.kb-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.kb-radio-item {
  margin-right: 0 !important;
  margin-bottom: 10px;
}

.kb-radio-item .el-radio__label {
  padding-left: 8px;
}
</style> 