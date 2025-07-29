<template>
  <div class="knowledge-qa-view">
    <div class="header">
      <h2 class="main-title">知识库问答</h2>
      <p class="subtitle">基于知识库的智能问答，快速获取准确信息</p>
    </div>

    <!-- 搜索输入区域 -->
    <div class="search-section">
      <div class="search-container">
        <el-input
          v-model="query"
          type="textarea"
          :rows="4"
          placeholder="请输入您的问题..."
          resize="none"
          class="search-input"
          @keyup.enter.ctrl="handleSearch"
        />
        
        <!-- 知识库选择 -->
        <div class="kb-selection-wrapper">
          <el-form-item label="选择知识库" class="kb-selection">
            <div v-if="kbLoading" class="kb-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>正在加载知识库列表...</span>
            </div>
            <div v-else-if="kbError" class="kb-error">
              <el-icon><Warning /></el-icon>
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
              <div class="form-tip">选择要用于问答的知识库。</div>
            </template>
          </el-form-item>
        </div>
        
        <div class="search-actions">
          <el-button 
            type="primary" 
            :loading="isLoading"
            @click="handleSearch"
            class="search-button"
          >
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </div>
      </div>
    </div>

    <!-- 使用说明 -->
    <div class="instructions-section">
      <el-card class="instructions-card">
        <template #header>
          <div class="card-header">
            <span>使用说明</span>
          </div>
        </template>
        <div class="instructions-content">
          <ul>
            <li>在搜索框中输入您的问题，支持多行输入</li>
            <li>选择要使用的知识库</li>
            <li>点击搜索按钮或按 Ctrl+Enter 开始搜索</li>
            <li>系统将基于知识库内容为您提供准确答案</li>
            <li>同时展示相关文档和问题建议</li>
          </ul>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Search, Loading, Warning, InfoFilled } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

const router = useRouter();

// 响应式数据
const query = ref('');
const isLoading = ref(false);

// 知识库相关
const kbLoading = ref(false);
const kbError = ref('');
const knowledgeBases = ref([]);
const selectedKbId = ref('');

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

// 加载知识库列表
const loadKnowledgeBases = async () => {
  kbLoading.value = true;
  kbError.value = '';
  
  try {
    const token = await login();
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
    console.error('加载知识库失败:', err);
    kbError.value = err.message || '加载知识库失败';
  } finally {
    kbLoading.value = false;
  }
};

// 组件挂载时加载知识库列表
onMounted(async () => {
  try {
    await loadKnowledgeBases();
  } catch (err) {
    console.error('初始化知识库列表失败:', err);
  }
});

// 处理搜索
const handleSearch = () => {
  if (!query.value.trim() || isLoading.value) return;

  // 检查是否选择了知识库
  if (!selectedKbId.value) {
    ElMessage.warning('请先选择知识库');
    return;
  }

  isLoading.value = true;
  
  // 跳转到结果页面，传递问题参数和知识库ID
  router.push({
    path: '/knowledge-qa-result',
    query: { 
      question: query.value.trim(),
      selectedKbId: selectedKbId.value
    }
  });
};
</script>

<style scoped>
.knowledge-qa-view {
  max-width: 800px;
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

.search-section {
  margin-bottom: 40px;
}

.search-container {
  background: #fff;
  border: 1px solid #e8eaed;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.2s ease;
}

.search-container:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.search-input {
  margin-bottom: 20px;
}

.search-input :deep(.el-textarea__inner) {
  border: none;
  border-radius: 8px;
  padding: 16px;
  font-size: 16px;
  resize: none;
  background: #f8f9fa;
  line-height: 1.5;
}

.search-input :deep(.el-textarea__inner:focus) {
  background: #fff;
  box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.2);
}

.kb-selection-wrapper {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: #fafbfc;
  border-radius: 6px;
  border: 1px solid #e8eaed;
  border-top: none;
  margin-top: -8px;
}

.kb-selection {
  margin-bottom: 0;
}

.kb-selection :deep(.el-form-item__label) {
  font-weight: 500;
  color: #5f6368;
  margin-bottom: 6px;
  font-size: 0.9rem;
}

.kb-loading, .kb-error, .kb-empty {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 0;
  color: #5f6368;
  font-size: 0.85rem;
}

.kb-error {
  color: #d93025;
}

.kb-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.kb-radio-item {
  margin-right: 0 !important;
  margin-bottom: 6px;
}

.kb-radio-item :deep(.el-radio__input) {
  margin-right: 4px;
}

.kb-radio-item .el-radio__label {
  padding-left: 4px;
  font-size: 0.85rem;
  color: #5f6368;
}

.kb-radio-item :deep(.el-radio__inner) {
  width: 14px;
  height: 14px;
}

.kb-radio-item :deep(.el-radio__inner::after) {
  width: 6px;
  height: 6px;
}

.form-tip {
  color: #9aa0a6;
  font-size: 0.75rem;
  margin-top: 3px;
}

.search-actions {
  display: flex;
  justify-content: flex-end;
}

.search-button {
  padding: 12px 24px;
  font-size: 16px;
  background-color: #1a73e8;
  border-color: #1a73e8;
  transition: all 0.2s ease;
}

.search-button:hover {
  background-color: #1557b0;
  border-color: #1557b0;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3);
}

.search-button:active {
  transform: translateY(0);
}

.instructions-section {
  margin-top: 40px;
}

.instructions-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  font-weight: 600;
  color: #333;
}

.instructions-content ul {
  margin: 0;
  padding-left: 20px;
  color: #666;
  line-height: 1.8;
}

.instructions-content li {
  margin-bottom: 8px;
}

@media (max-width: 768px) {
  .knowledge-qa-view {
    padding: 16px;
  }
  
  .main-title {
    font-size: 1.8rem;
  }
  
  .search-container {
    padding: 16px;
  }
}
</style> 