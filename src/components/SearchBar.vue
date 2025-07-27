<template>
  <div class="search-wrapper">
    <div class="search-container">
      <div class="search-input-group">
        <el-input
          v-model="query"
          type="textarea"
          :rows="4"
          placeholder="搜索、提问或发消息"
          resize="none"
          class="custom-input"
        />
      </div>
      
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
          <el-radio-group v-else v-model="selectedKbId" class="kb-radio-group" @change="handleKbChange">
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
            <div class="form-tip">选择要用于搜索的知识库。</div>
          </template>
        </el-form-item>
      </div>
      
      <div class="search-actions">
        <el-button 
          type="primary" 
          @click="onSearch"
          class="submit-button"
        >
          <el-icon><ArrowUp /></el-icon>
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ArrowUp, Loading, Warning, InfoFilled } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const query = ref('');

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

// 处理知识库选择变化
const handleKbChange = () => {
  console.log('选择知识库:', selectedKbId.value);
};

// 组件挂载时加载知识库
onMounted(async () => {
  try {
    await loadKnowledgeBases();
  } catch (err) {
    console.error('初始化知识库列表失败:', err);
  }
});

const onSearch = () => {
  if (query.value.trim()) {
    // 检查是否选择了知识库
    if (!selectedKbId.value) {
      alert('请先选择知识库');
      return;
    }
    
    // 将查询内容和选中的知识库ID作为参数传递到聊天界面
    router.push({
      path: '/chat',
      query: { 
        initialMessage: query.value,
        selectedKbId: selectedKbId.value
      }
    });
  }
};
</script>

<style scoped>
.search-wrapper {
  max-width: 650px;
  width: 100%;
}

.search-container {
  width: 100%;
  padding: 20px;
  background-color: #ffffff;
  border: 1px solid #e8eaed;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  position: relative;
  transition: box-shadow 0.2s ease;
}

.search-container:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.search-input-group {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
  border: none;
  padding-left: 0;
  margin-left: 0;
}

.search-input-group .el-input {
  flex: 1;
}

.kb-selection-wrapper {
  margin-bottom: 16px;
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

/* 使用>>>深度选择器彻底去除边框 */
.search-input-group .custom-input >>> .el-textarea__inner {
  border: 0;
  border-radius: 8px;
  padding: 0;
  box-shadow: none !important;
  resize: none;
  background: transparent;
  font-size: 16px;
  line-height: 1.5;
  /* 自定义滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: rgba(144, 147, 153, 0.3) transparent;
}

/* 针对Webkit浏览器（Chrome、Safari等）的滚动条样式 */
.search-input-group .custom-input >>> .el-textarea__inner::-webkit-scrollbar {
  width: 6px;
}

.search-input-group .custom-input >>> .el-textarea__inner::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.search-input-group .custom-input >>> .el-textarea__inner::-webkit-scrollbar-thumb {
  background-color: #c0c4cc;
  border-radius: 10px;
  border: 1px solid #f1f1f1;
}

.search-input-group .custom-input >>> .el-textarea__inner::-webkit-scrollbar-thumb:hover {
  background-color: #909399;
}

/* 去掉上下箭头 */
.search-input-group .custom-input >>> .el-textarea__inner::-webkit-scrollbar-button {
  display: none;
}

.search-input-group .custom-input >>> .el-textarea__wrapper {
  box-shadow: none !important;
  border: 0;
  padding: 0;
  background: transparent;
}

.search-input-group .custom-input >>> .el-textarea__wrapper.is-focus {
  box-shadow: none !important;
  border: 0;
  background: transparent;
}

.search-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.submit-button {
  background-color: #1a73e8;
  border: none;
  color: #ffffff;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 80px;
  justify-content: center;
}

.submit-button:hover {
  background-color: #1557b0;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3);
}

.submit-button:active {
  transform: translateY(0);
}

@media (max-width: 768px) {
  .search-options {
    justify-content: space-between;
  }
  
  .search-options .el-button {
    margin-right: 0;
    flex-grow: 1;
    margin-bottom: 0;
  }
}
</style>
