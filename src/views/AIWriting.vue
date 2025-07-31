<template>
  <div class="ai-writing-view">
    <div class="header">
      <h2 class="main-title">AI 写作</h2>
      <p class="subtitle">智能文章续写与润色，助力高效写作</p>
    </div>
    <el-row justify="center">
      <el-col :xs="24" :sm="22" :md="22" :lg="18" :xl="20" style="max-width: 1100px;">
        <el-card class="gen-card">
          <!-- Tab 切换按钮 -->
          <div class="tab-btns" style="text-align:center; margin-bottom: 24px;">
            <el-button :type="aiType === 'xuxie' ? 'primary' : 'default'" @click="aiType = 'xuxie'">文章续写</el-button>
            <el-button :type="aiType === 'runse' ? 'primary' : 'default'" @click="aiType = 'runse'" style="margin-left: 10px;">文章润色</el-button>
          </div>
          <el-form ref="formRef" :model="form" :rules="rules" class="form-section" label-width="100px" label-position="top">
            <el-form-item label="指令 instruction" prop="instruction">
              <el-input v-model="form.instruction" clearable placeholder="请输入写作指令，如风格、要求等" />
              <template #description>
                <div class="form-tip">指令为可选项，可指定写作风格、语言等。</div>
              </template>
            </el-form-item>
            <el-form-item label="上传文件" prop="fileContent" required>
              <el-upload
                class="upload-demo"
                :show-file-list="false"
                :auto-upload="false"
                :before-upload="() => false"
                accept=".txt,.docx"
                @change="handleFileChange"
              >
                <el-button type="primary">选择文件</el-button>
                <span v-if="fileName" class="file-name"><el-icon><Document /></el-icon> 已上传: {{ fileName }}</span>
              </el-upload>
              <template #description>
                <div class="form-tip">仅支持 txt 或 docx 文件。</div>
              </template>
            </el-form-item>
            <!-- 仅续写时显示知识库选择 -->
            <el-form-item v-if="aiType === 'xuxie'" label="选择知识库" class="kb-selection">
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
                <div class="form-tip">选择要用于续写的知识库（可选）。</div>
              </template>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="generateContent" style="width: 100%;">生成写作内容</el-button>
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
                <h3>正在生成内容</h3>
                <p>AI正在为您生成高质量文本...</p>
                <div class="loading-dots">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="generatedText" class="result-card">
            <div class="result-header">
              <span class="result-title">生成结果</span>
            </div>
            <el-divider class="result-divider" />
            <div style="white-space: pre-wrap;">{{ generatedText }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Document, Loading, WarningFilled, InfoFilled } from '@element-plus/icons-vue';
import mammoth from 'mammoth';

const router = useRouter();

const form = ref({
  instruction: '',
  fileContent: ''
});
const fileName = ref('');
const loading = ref(false);
const generatedText = ref('');
const formRef = ref();

const rules = {
  fileContent: [
    { required: true, message: '请上传文件', trigger: 'change' }
  ]
};

// 新增：AI写作类型，默认为润色
const aiType = ref('xuxie'); // 'runse' 润色, 'xuxie' 续写

// 知识库相关
const knowledgeBases = ref([]);
const selectedKbId = ref('');
const kbLoading = ref(false);
const kbError = ref('');

// 登录函数
const login = async () => {
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
  return token;
};

async function loadKnowledgeBases() {
  kbLoading.value = true;
  kbError.value = '';
  try {
    // 使用login函数获取token
    const token = await login();
    
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
    if (data.code === 0 && data.data && data.data.kbs) {
      knowledgeBases.value = data.data.kbs.map(kb => ({
        id: kb.id,
        name: kb.name || `知识库 ${kb.id}`
      }));
    } else {
      knowledgeBases.value = [];
    }
  } catch (err) {
    kbError.value = err.message || '加载知识库失败';
  } finally {
    kbLoading.value = false;
  }
}

onMounted(() => {
  loadKnowledgeBases();
});

async function handleFileChange(fileEvent) {
  let file = fileEvent.raw || fileEvent.target?.files?.[0] || fileEvent;
  if (!file) return;
  fileName.value = file.name;
  if (file.type === 'text/plain') {
    const reader = new FileReader();
    reader.onload = (e) => {
      form.value.fileContent = e.target.result;
    };
    reader.readAsText(file);
  } else if (
    file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ) {
    const arrayBuffer = await file.arrayBuffer();
    const { value } = await mammoth.extractRawText({ arrayBuffer });
    form.value.fileContent = value;
  } else {
    form.value.fileContent = '';
    fileName.value = '';
    alert('仅支持 txt 或 docx 文件');
  }
}

// 新增：AI写作后端请求主流程
async function requestAIWriting({ type, instruction, article, kbId }) {
  // 1. 登录
  const loginData = {
    email: '123@123.com',
    password: 'hXWqKtPnAt+tvQeaKHh87nNc5xbuVJu5thZtH1gBOzFfwmjml8DJp3/E2HzILWJVqWy3Vp79g3wPC67+ImkG1IQyvD4BSYXp4zlUy++toYQO1GOEMys4Xn8Xta2G9KTkjhWrR9qfOyEroIIzXEy2+HBf4DenGXPABLIh0HAGlZSdizpq3mHbIhHm26CDl0OIT7S7xd6YCOYpM9VC6IMYQI/a3r5qZc8cIvkQGrEnrhlPVIPQocxY5shmXwaEJxugPd/kezvsienh6TEfctqVcSwIssIgPBunOVJb2PDCF/NevwS3ZGqmFn7VIxUwHi0oz4KYZsudj+K8aJqG/8Jj8w=='
  };
  const loginResp = await fetch('http://127.0.0.1/v1/user/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(loginData)
  });
  if (!loginResp.ok) throw new Error('登录失败');
  let token = loginResp.headers.get('Authorization');
  if (!token) {
    const body = await loginResp.json();
    token = body.data?.access_token;
  }
  if (!token) throw new Error('未获取到token');

  // 2. 第一次set，空DSL，获取id和title
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
  };
  const setResp1 = await fetch('http://127.0.0.1/v1/canvas/set', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token
    },
    body: JSON.stringify(emptySetPayload)
  });
  if (!setResp1.ok) throw new Error('首次set接口失败');
  const setJson1 = await setResp1.json();
  const unique_id = setJson1.data?.id;
  const set_title = setJson1.data?.title;
  if (!unique_id || !set_title) throw new Error('首次set未返回id或title');

  // 3. 用public下的 dsl 文件内容，带id和title再次set
  const dslFile = type === 'runse' ? '/dsl_aiwriting_runse.json' : '/dsl_aiwriting_xuxie.json';
  const dslResp = await fetch(dslFile);
  if (!dslResp.ok) throw new Error('dsl.json 读取失败');
  const dslData = await dslResp.json();
  dslData.id = unique_id;
  dslData.title = set_title;

  // 4. 替换 dsl 中 query 字段
  // components.begin.obj.params.query
  const queryList = dslData.dsl?.components?.begin?.obj?.params?.query || [];
  for (const q of queryList) {
    if (q.key === 'instruction') q.value = instruction;
    if (q.key === 'article') q.value = article;
  }
  // graph.nodes[].data.form.query
  const nodes = dslData.dsl?.graph?.nodes || [];
  for (const node of nodes) {
    const formObj = node.data?.form;
    if (formObj && Array.isArray(formObj.query)) {
      for (const q of formObj.query) {
        if (q.key === 'instruction') q.value = instruction;
        if (q.key === 'article') q.value = article;
      }
      // 仅续写时添加知识库ID
      if (type === 'xuxie' && formObj.kb_ids !== undefined && kbId) {
        formObj.kb_ids = [kbId];
      }
    }
  }

  // 5. set 提交修改后的 dsl
  const setResp2 = await fetch('http://127.0.0.1/v1/canvas/set', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token
    },
    body: JSON.stringify(dslData)
  });
  if (!setResp2.ok) throw new Error('第二次set接口失败');

  // 6. reset
  const resetResp = await fetch('http://127.0.0.1/v1/canvas/reset', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token
    },
    body: JSON.stringify({ id: unique_id })
  });
  if (!resetResp.ok) throw new Error('reset接口失败');

  // 7. completion（流式处理）- 重新获取token
  const freshToken = await login();
  const completionResp = await fetch('http://127.0.0.1/v1/canvas/completion', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': freshToken
    },
    body: JSON.stringify({ id: unique_id })
  });
  if (!completionResp.ok) throw new Error('completion接口失败');

  // === 流式处理核心 ===
  const reader = completionResp.body.getReader();
  const decoder = new TextDecoder();
  let done = false;
  let buffer = '';
  let finalAnswer = '';
  try {
    while (!done) {
      const { value, done: readerDone } = await reader.read();
      done = readerDone;
      if (value) {
        const text = decoder.decode(value, { stream: true });
        buffer += text;
        let lines = buffer.split('\n');
        buffer = lines.pop(); // 最后一行可能不完整
        for (const line of lines) {
          if (line.startsWith('data:')) {
            const dataStr = line.substring(5).trim();
            if (dataStr === '[DONE]' || !dataStr) continue;
            try {
              const data = JSON.parse(dataStr);
              
              // 检查是否有错误
              if (data.code && data.code !== 0) {
                console.error('AIWriting completion 流式响应中的错误:', data);
                throw new Error(data.message || '请求失败');
              }
              
              // 只有当answer存在且running_status不为true时才展示
              if (data.data && data.data.answer && data.data.running_status !== true) {
                console.log('AIWriting completion 返回内容:', data.data);
                generatedText.value = data.data.answer;
                finalAnswer = data.data.answer;
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
              
              // 不是完整JSON，拼回buffer，等下次
              buffer = line + '\n' + buffer;
              break;
            }
          }
        }
      }
    }
    // 控制台输出最终内容
    console.log('AIWriting completion 最终内容:', finalAnswer);
    if (type === 'xuxie') {
      // 续写：拼接原文和生成内容
      const original = article || '';
      const result = (original.endsWith('\n') ? original : original + '\n') + (finalAnswer || '');
      generatedText.value = '生成完成，即将跳转';
      setTimeout(() => {
        router.push({ path: '/report-result', query: { report: result, from: 'aiwriting' } });
      }, 500);
      return result;
    } else {
      // 润色：只展示生成内容
      generatedText.value = '生成完成，即将跳转';
      setTimeout(() => {
        router.push({ path: '/report-result', query: { report: finalAnswer, from: 'aiwriting' } });
      }, 500);
      return finalAnswer;
    }
  } catch (e) {
    // 只有整体异常才报错
    generatedText.value = '生成失败，请重试：' + (e?.message || e);
    throw e;
  }
}

const generateContent = () => {
  formRef.value.validate(async (valid) => {
    if (!valid) return;
    loading.value = true;
    generatedText.value = '';
    try {
      // 选择类型：runse 润色，xuxie 续写
      const type = aiType.value;
      const instruction = form.value.instruction;
      const article = form.value.fileContent;
      const kbId = type === 'xuxie' ? selectedKbId.value : undefined;
      await requestAIWriting({ type, instruction, article, kbId });
      generatedText.value = '生成完成，即将跳转';
    } catch (e) {
      generatedText.value = '生成失败，请重试：' + (e?.message || e);
    } finally {
      loading.value = false;
    }
  });
};
</script>

<style scoped>
.ai-writing-view {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}
.header {
  text-align: center;
  margin-bottom: 40px;
}
.main-title {
  font-size: 2.2rem;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}
.subtitle {
  font-size: 1rem;
  color: #999;
  margin: 0;
}
.gen-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(64,158,255,0.08);
  background: #fff;
  margin-bottom: 32px;
  padding: 24px 24px 0 24px;
  transition: box-shadow 0.2s;
}
.gen-card:hover {
  box-shadow: 0 6px 24px rgba(64,158,255,0.13);
}
.form-section {
  margin-bottom: 0;
  padding: 24px 24px 0 24px;
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
.result-title {
  font-weight: 600;
}
.result-divider {
  margin: 8px 0 18px 0;
}
.loading-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
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
.kb-selection {
  margin-top: 20px;
}
.kb-loading, .kb-error, .kb-empty {
  padding: 10px 15px;
  border-radius: 8px;
  background-color: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #faecd8;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.kb-radio-group {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 12px;
}
.kb-radio-item {
  padding: 8px 15px;
  border-radius: 6px;
  border: 1px solid #dcdfe6;
  transition: all 0.3s;
  margin-right: 0 !important;
  margin-bottom: 0 !important;
}
.kb-radio-item:hover {
  background-color: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}
.kb-radio-item.is-checked {
  background-color: #ffffff;
  border-color: #409eff;
  color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}
@media (max-width: 1200px) {
  .ai-writing-view {
    max-width: 100%;
  }
}
@media (max-width: 768px) {
  .ai-writing-view {
    padding: 16px;
  }
  .main-title {
    font-size: 1.8rem;
  }
  .gen-card {
    padding: 16px 8px 0 8px;
  }
}
</style> 