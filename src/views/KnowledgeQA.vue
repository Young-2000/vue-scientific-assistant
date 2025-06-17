<template>
  <div class="knowledge-qa-view">
    <h2 class="main-title">知识库问答</h2>
    <p class="subtitle">专业面向预设知识库或私人知识库，支持多轮问答，具备文档定位能力</p>

    <div class="qa-container">
      <!-- 左侧知识库选择区域 -->
      <div class="knowledge-base-panel">
        <h3>知识库选择</h3>
        
        <!-- 知识库选项卡 -->
        <el-tabs v-model="activeKnowledgeBase" @tab-click="handleKnowledgeBaseChange">
          <el-tab-pane label="预设知识库" name="preset">
            <div class="knowledge-base-list">
              <el-radio-group v-model="selectedPresetKB" size="large">
                <el-radio v-for="kb in presetKnowledgeBases" :key="kb.id" :label="kb.id" border>
                  {{ kb.name }}
                </el-radio>
              </el-radio-group>
            </div>
          </el-tab-pane>
          <el-tab-pane label="我的知识库" name="personal">
            <div v-if="personalKnowledgeBases.length > 0" class="knowledge-base-list">
              <el-radio-group v-model="selectedPersonalKB" size="large">
                <el-radio v-for="kb in personalKnowledgeBases" :key="kb.id" :label="kb.id" border>
                  {{ kb.name }}
                </el-radio>
              </el-radio-group>
            </div>
            <div v-else class="empty-kb">
              <el-empty description="暂无个人知识库" />
              <el-button type="primary" @click="showUploadDialog">
                <el-icon><Plus /></el-icon>
                创建知识库
              </el-button>
            </div>
          </el-tab-pane>
        </el-tabs>

        <!-- 知识库详情 -->
        <div v-if="currentKnowledgeBase" class="kb-details">
          <h4>{{ currentKnowledgeBase.name }}</h4>
          <p>{{ currentKnowledgeBase.description }}</p>
          <div class="kb-stats">
            <div class="stat-item">
              <span class="stat-label">文档数量</span>
              <span class="stat-value">{{ currentKnowledgeBase.documentCount }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">更新时间</span>
              <span class="stat-value">{{ currentKnowledgeBase.lastUpdated }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧对话区域 -->
      <div class="chat-panel">
        <div class="chat-messages" ref="chatContainer">
          <div v-for="(message, index) in chatMessages" :key="index" 
            :class="['message', message.role === 'user' ? 'user-message' : 'assistant-message']">
            <div class="message-content">
              <div class="message-text">{{ message.content }}</div>
              <div v-if="message.sources && message.sources.length > 0" class="message-sources">
                <p class="sources-title">参考来源：</p>
                <el-tag 
                  v-for="(source, idx) in message.sources" 
                  :key="idx"
                  size="small"
                  effect="plain"
                  @click="viewSource(source)"
                >
                  {{ source.title }}
                </el-tag>
              </div>
            </div>
          </div>
          <div v-if="isLoading" class="loading-indicator">
            <el-icon class="is-loading"><Loading /></el-icon>
            正在思考...
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input">
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="3"
            placeholder="请输入您的问题..."
            @keyup.enter.ctrl="sendMessage"
          />
          <div class="input-actions">
            <el-tooltip content="上传相关文档" placement="top">
              <el-button circle @click="uploadDocument">
                <el-icon><Upload /></el-icon>
              </el-button>
            </el-tooltip>
            <el-button type="primary" @click="sendMessage" :disabled="!userInput.trim() || isLoading">
              发送
              <el-icon class="el-icon--right"><Position /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传知识库对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="创建知识库" width="500px">
      <el-form :model="newKnowledgeBase" label-width="100px">
        <el-form-item label="知识库名称">
          <el-input v-model="newKnowledgeBase.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="知识库描述">
          <el-input v-model="newKnowledgeBase.description" type="textarea" :rows="3" placeholder="请输入知识库描述" />
        </el-form-item>
        <el-form-item label="上传文档">
          <el-upload
            action="#"
            multiple
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="fileList"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持PDF、Word、TXT等格式文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createKnowledgeBase" :loading="isCreating">
            创建
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 文档源查看对话框 -->
    <el-dialog v-model="sourceDialogVisible" :title="currentSource.title" width="70%">
      <div class="source-content">
        <div class="source-info">
          <p><strong>文件名：</strong>{{ currentSource.filename }}</p>
          <p><strong>页码：</strong>{{ currentSource.page }}</p>
        </div>
        <div class="source-text">
          <p>{{ currentSource.content }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Plus, Upload, Position, Loading } from '@element-plus/icons-vue';

// 知识库数据
const presetKnowledgeBases = [
  { 
    id: 'science', 
    name: '科学研究库', 
    description: '包含各领域科学研究论文、报告和分析',
    documentCount: 5280,
    lastUpdated: '2023-10-15'
  },
  { 
    id: 'tech', 
    name: '技术文档库', 
    description: '各类技术文档、规范和标准',
    documentCount: 3150,
    lastUpdated: '2023-11-02'
  },
  { 
    id: 'medicine', 
    name: '医学知识库', 
    description: '医学研究论文、临床指南和医疗资料',
    documentCount: 4720,
    lastUpdated: '2023-10-28'
  }
];

const personalKnowledgeBases = ref([
  // 用户可能已有的个人知识库
]);

// 状态变量
const activeKnowledgeBase = ref('preset');
const selectedPresetKB = ref('science');
const selectedPersonalKB = ref('');
const userInput = ref('');
const chatMessages = ref([
  { 
    role: 'assistant', 
    content: '您好！我是基于知识库的智能助手。请选择一个知识库并提问，我将为您查找相关信息。',
    sources: []
  }
]);
const isLoading = ref(false);
const uploadDialogVisible = ref(false);
const sourceDialogVisible = ref(false);
const newKnowledgeBase = ref({
  name: '',
  description: ''
});
const fileList = ref([]);
const isCreating = ref(false);
const currentSource = ref({
  title: '',
  filename: '',
  page: '',
  content: ''
});
const chatContainer = ref(null);

// 计算当前选择的知识库
const currentKnowledgeBase = computed(() => {
  if (activeKnowledgeBase.value === 'preset') {
    return presetKnowledgeBases.find(kb => kb.id === selectedPresetKB.value);
  } else {
    return personalKnowledgeBases.value.find(kb => kb.id === selectedPersonalKB.value);
  }
});

// 切换知识库类型
const handleKnowledgeBaseChange = () => {
  // 可以在这里添加切换逻辑
};

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;
  
  // 添加用户消息
  chatMessages.value.push({
    role: 'user',
    content: userInput.value,
    sources: []
  });
  
  // 清空输入框
  const userQuestion = userInput.value;
  userInput.value = '';
  
  // 滚动到底部
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
  
  // 显示加载状态
  isLoading.value = true;
  
  // 模拟API调用延迟
  setTimeout(() => {
    // 添加助手回复
    const kbName = currentKnowledgeBase.value ? currentKnowledgeBase.value.name : '未选择知识库';
    
    let responseMessage;
    if (userQuestion.includes('深度学习') || userQuestion.includes('机器学习')) {
      responseMessage = {
        role: 'assistant',
        content: '深度学习是机器学习的一个分支，它使用多层神经网络来模拟人脑的学习过程。与传统机器学习相比，深度学习能够自动从大量数据中学习特征，无需手动特征工程。它在图像识别、自然语言处理和语音识别等领域取得了突破性进展。',
        sources: [
          {
            title: '深度学习概述',
            filename: 'deep_learning_intro.pdf',
            page: '15-17',
            content: '深度学习是机器学习的一个子领域，专注于使用人工神经网络进行学习。这些网络被称为"深度"是因为它们包含多个隐藏层。深度学习已经在计算机视觉、语音识别、自然语言处理、音频识别和生物信息学等领域取得了重大突破，在某些情况下甚至超过了人类的表现。'
          },
          {
            title: '深度学习与传统机器学习的比较',
            filename: 'ml_vs_dl.pdf',
            page: '42',
            content: '与传统机器学习方法相比，深度学习的主要优势在于其能够自动执行特征提取过程。在传统机器学习中，特征工程通常需要领域专家的知识和大量的人工工作。而深度学习算法可以通过学习过程自动发现数据中的模式和特征。'
          }
        ]
      };
    } else if (userQuestion.includes('量子计算') || userQuestion.includes('量子')) {
      responseMessage = {
        role: 'assistant',
        content: '量子计算是一种利用量子力学现象（如叠加和纠缠）进行计算的技术。与经典计算机使用比特不同，量子计算机使用量子比特（qubit）。量子计算机有潜力解决某些经典计算机难以处理的问题，如大数分解、搜索无序数据库和模拟量子系统。',
        sources: [
          {
            title: '量子计算入门',
            filename: 'quantum_computing_basics.pdf',
            page: '8-10',
            content: '量子计算是利用量子力学原理进行信息处理的计算范式。与经典计算使用二进制位（0或1）不同，量子计算使用量子比特，它可以同时处于多个状态的叠加。这种特性使量子计算机在特定问题上具有显著的速度优势。'
          }
        ]
      };
    } else {
      responseMessage = {
        role: 'assistant',
        content: `我已在${kbName}中查找相关信息，但未找到与您问题直接相关的内容。您可以尝试重新表述问题，或者选择其他知识库。`,
        sources: []
      };
    }
    
    chatMessages.value.push(responseMessage);
    isLoading.value = false;
    
    // 滚动到底部
    nextTick(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
      }
    });
  }, 2000);
};

// 上传相关文档
const uploadDocument = () => {
  ElMessage.info('文档上传功能已触发，可以在此处理文档上传逻辑');
};

// 显示上传对话框
const showUploadDialog = () => {
  uploadDialogVisible.value = true;
  newKnowledgeBase.value = {
    name: '',
    description: ''
  };
  fileList.value = [];
};

// 处理文件变化
const handleFileChange = (file) => {
  ElMessage.success(`文件 ${file.name} 已选择`);
};

// 创建知识库
const createKnowledgeBase = () => {
  if (!newKnowledgeBase.value.name) {
    ElMessage.warning('请输入知识库名称');
    return;
  }
  
  if (fileList.value.length === 0) {
    ElMessage.warning('请至少上传一个文档');
    return;
  }
  
  isCreating.value = true;
  
  // 模拟创建过程
  setTimeout(() => {
    const newKB = {
      id: 'personal-' + Date.now(),
      name: newKnowledgeBase.value.name,
      description: newKnowledgeBase.value.description || '个人知识库',
      documentCount: fileList.value.length,
      lastUpdated: new Date().toLocaleDateString()
    };
    
    personalKnowledgeBases.value.push(newKB);
    selectedPersonalKB.value = newKB.id;
    activeKnowledgeBase.value = 'personal';
    
    ElMessage.success('知识库创建成功');
    uploadDialogVisible.value = false;
    isCreating.value = false;
  }, 2000);
};

// 查看来源文档
const viewSource = (source) => {
  currentSource.value = source;
  sourceDialogVisible.value = true;
};

// 组件挂载时滚动到底部
onMounted(() => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
});
</script>

<style scoped>
.knowledge-qa-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.main-title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.subtitle {
  font-size: 1rem;
  color: #666;
  margin-bottom: 30px;
}

.qa-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
}

.knowledge-base-panel {
  flex: 0 0 300px;
  border-right: 1px solid #eee;
  padding-right: 20px;
  overflow-y: auto;
}

.chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 20px;
}

.message {
  margin-bottom: 15px;
  display: flex;
}

.user-message {
  justify-content: flex-end;
}

.message-content {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 8px;
  word-break: break-word;
}

.user-message .message-content {
  background: #e6f7ff;
  color: #0076ff;
}

.assistant-message .message-content {
  background: #f2f2f2;
  color: #333;
}

.message-sources {
  margin-top: 8px;
  font-size: 0.9em;
}

.sources-title {
  color: #666;
  margin-bottom: 4px;
}

.el-tag {
  margin-right: 5px;
  margin-bottom: 5px;
  cursor: pointer;
}

.chat-input {
  margin-top: auto;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.knowledge-base-list {
  margin-top: 15px;
}

.el-radio {
  margin-bottom: 10px;
  width: 100%;
}

.kb-details {
  margin-top: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.kb-details h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

.kb-details p {
  color: #666;
  margin-bottom: 15px;
}

.kb-stats {
  display: flex;
  justify-content: space-between;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.9em;
  color: #999;
}

.stat-value {
  font-weight: bold;
  color: #333;
}

.empty-kb {
  padding: 20px;
  text-align: center;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #999;
  padding: 10px;
}

.source-content {
  max-height: 500px;
  overflow-y: auto;
}

.source-info {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.source-text {
  white-space: pre-wrap;
  line-height: 1.6;
}
</style> 