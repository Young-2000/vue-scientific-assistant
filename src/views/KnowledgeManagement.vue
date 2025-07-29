<template>
  <div class="knowledge-management-view">
    <div class="header">
      <h2 class="main-title">知识库管理</h2>
      <p class="subtitle">管理您的知识库，上传文档，配置问答设置</p>
    </div>

    <!-- 操作按钮区域 -->
    <div class="actions-section">
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建知识库
      </el-button>
    </div>

    <!-- 知识库统计 -->
    <KnowledgeBaseStats 
      :knowledge-bases="knowledgeBases" 
      ref="statsRef"
    />

    <!-- 知识库过滤 -->
    <KnowledgeBaseFilter 
      :knowledge-bases="knowledgeBases" 
      @filtered="handleFiltered"
      ref="filterRef"
    />

    <!-- 知识库列表 -->
    <div class="kb-list-section">
      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在加载知识库列表...</span>
      </div>
      
      <div v-else-if="error" class="error-container">
        <el-icon><Warning /></el-icon>
        <span>{{ error }}</span>
        <el-button type="primary" link @click="loadKnowledgeBases">重试</el-button>
      </div>
      
      <div v-else-if="knowledgeBases.length === 0" class="empty-container">
        <el-icon><FolderOpened /></el-icon>
        <span>暂无知识库，点击上方按钮创建第一个知识库</span>
      </div>
      
      <div v-else class="kb-grid">
        <el-card 
          v-for="kb in filteredKnowledgeBases" 
          :key="kb.id || `kb-${kb.name}-${kb.created_at}`" 
          class="kb-card"
          shadow="hover"
        >
          <template #header>
            <div class="kb-card-header">
              <div class="kb-title">
                <el-icon><Document /></el-icon>
                <span>{{ kb.name }}</span>
              </div>
              <div class="kb-actions">
                <el-dropdown @command="handleKbAction">
                  <el-button type="text" size="small">
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{ action: 'edit', kb }">
                        <el-icon><Edit /></el-icon>编辑
                      </el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'documents', kb }">
                        <el-icon><Files /></el-icon>文档管理
                      </el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'delete', kb }" divided>
                        <el-icon><Delete /></el-icon>删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </template>
          
          <div class="kb-content">
            <div class="kb-info">
              <div class="info-item">
                <span class="label">ID:</span>
                <span class="value">{{ kb.id }}</span>
              </div>
              <div class="info-item">
                <span class="label">更新时间:</span>
                <span class="value">{{ formatDate(kb.update_time) }}</span>
              </div>
              <div class="info-item">
                <span class="label">文档数量:</span>
                <span class="value">{{ kb.doc_num || 0 }}</span>
              </div>

            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 创建/编辑知识库对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingKb ? '编辑知识库' : '创建知识库'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="kbFormRef"
        :model="kbForm"
        :rules="kbFormRules"
        label-width="100px"
      >
        <el-form-item label="知识库名称" prop="name">
          <el-input v-model="kbForm.name" placeholder="请输入知识库名称" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitKbForm">
          {{ editingKb ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 文档管理对话框 -->
    <el-dialog
      v-model="showDocumentsDialog"
      title="文档管理"
      width="800px"
      @close="resetDocumentForm"
    >
      <div v-if="currentKb" class="documents-container">
        <div class="documents-header">
          <h4>{{ currentKb.name }} - 文档列表</h4>
          <el-button type="primary" @click="showUploadDialog = true">
            <el-icon><Upload /></el-icon>
            上传文档
          </el-button>
        </div>
        
        <div class="documents-list">
          <!-- 批量操作按钮 -->
          <div v-if="selectedDocuments.length > 0" class="batch-actions">
            <el-button 
              type="primary" 
              size="small" 
              @click="batchParseDocuments"
              :loading="batchParsing"
              :disabled="!canBatchParse"
            >
              <el-icon><Files /></el-icon>
              批量解析 ({{ selectedDocuments.length }})
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="batchDeleteDocuments"
              :loading="batchDeleting"
            >
              <el-icon><Delete /></el-icon>
              批量删除 ({{ selectedDocuments.length }})
            </el-button>
            <el-button size="small" @click="clearSelection">
              取消选择
            </el-button>
          </div>
          
          <div v-if="documentsLoading" class="loading-container">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在加载文档列表...</span>
          </div>
          
          <div v-else-if="documentsError" class="error-container">
            <el-icon><Warning /></el-icon>
            <span>{{ documentsError }}</span>
            <el-button type="primary" link @click="loadDocuments">重试</el-button>
          </div>
          
          <div v-else-if="documents.length === 0" class="empty-container">
            <el-icon><Document /></el-icon>
            <span>暂无文档，点击上方按钮上传文档</span>
          </div>
          
          <el-table ref="documentsTableRef" v-else :data="documents" style="width: 100%" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="name" label="文档名称">
              <template #default="{ row }">
                <el-button 
                  type="text" 
                  @click="previewDocument(row)"
                  class="document-name-button"
                >
                  <el-icon><View /></el-icon>
                  {{ row.name }}
                </el-button>
              </template>
            </el-table-column>
            <el-table-column prop="update_time" label="上传时间" width="150">
              <template #default="{ row }">
                {{ formatDate(row.update_time || row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="解析状态" width="150">
              <template #default="{ row }">
                <div>
                  <el-tag :type="getParseStatusType(row)" size="small">
                    {{ getParseStatusText(row) }}
                  </el-tag>
                  <div v-if="row.run === '1'" style="font-size: 12px; color: #666; margin-top: 4px;">
                    进度: {{ Math.round(row.progress * 100) }}%
                  </div>
                  <div v-if="row.run === '3' && row.chunk_num > 0" style="font-size: 12px; color: #666; margin-top: 4px;">
                    {{ row.chunk_num }}个块 / {{ row.token_num }}tokens
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="parseDocument(row)"
                  :loading="row.parsing"
                  :disabled="row.run === '1' || row.run === '3'"
                >
                  <el-icon><Files /></el-icon>
                  解析
                </el-button>
                <el-button type="danger" size="small" @click="deleteDocument(row)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 文档上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传文档"
      width="500px"
      @close="resetUploadForm"
    >
      <el-upload
        ref="uploadRef"
        :before-upload="beforeUpload"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :auto-upload="false"
        multiple
        drag
        accept=".pdf,.docx,.txt"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 PDF、DOCX、TXT 格式文件
          </div>
        </template>
      </el-upload>
      
      <!-- 上传按钮 -->
      <div class="upload-actions">
        <el-button type="primary" @click="handleUploadFiles" :loading="submitting" :disabled="uploadFileList.length === 0">
          <el-icon><Upload /></el-icon>
          上传文档
        </el-button>
        <el-button @click="clearUploadFiles" :disabled="uploadFileList.length === 0">
          清空文件
        </el-button>
      </div>
    </el-dialog>

    <!-- 文件预览组件 -->
    <FilePreview
      :visible="filePreviewVisible"
      :doc-id="selectedFile?.id"
      :file-name="selectedFile?.name"
      :file-type="getFileType(selectedFile?.name)"
      @close="closeFilePreview"
    />

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { 
  Plus, Loading, Warning, FolderOpened, Document, 
  MoreFilled, Edit, Files, Delete, Upload, UploadFilled, View
} from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import KnowledgeBaseStats from '@/components/KnowledgeBaseStats.vue';
import KnowledgeBaseFilter from '@/components/KnowledgeBaseFilter.vue';
import FilePreview from '@/components/FilePreview.vue';

// 响应式数据
const loading = ref(false);
const error = ref('');
const knowledgeBases = ref([]);
const showCreateDialog = ref(false);
const showDocumentsDialog = ref(false);
const showUploadDialog = ref(false);
const submitting = ref(false);
const editingKb = ref(null);
const currentKb = ref(null);
const documents = ref([]);
const documentsLoading = ref(false);
const documentsError = ref('');
const uploadFileList = ref([]);
const selectedDocuments = ref([]);
const batchParsing = ref(false);
const batchDeleting = ref(false);
const statsRef = ref();
const filterRef = ref();
const documentsTableRef = ref();
const filteredKnowledgeBases = ref([]);

// 文件预览相关
const filePreviewVisible = ref(false);
const selectedFile = ref(null);

// 表单数据
const kbFormRef = ref();
const kbForm = ref({
  name: ''
});

const kbFormRules = {
  name: [
    { required: true, message: '请输入知识库名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ]
};

// 计算属性
const canBatchParse = computed(() => {
  return selectedDocuments.value.some(doc => doc.run === '0' || doc.run === '2');
});

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
  loading.value = true;
  error.value = '';
  
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
      knowledgeBases.value = data.data.kbs;
    } else {
      knowledgeBases.value = [];
    }
  } catch (err) {
    console.error('加载知识库失败:', err);
    error.value = err.message || '加载知识库失败';
  } finally {
    loading.value = false;
  }
};



// 处理知识库操作
const handleKbAction = ({ action, kb }) => {
  switch (action) {
    case 'edit':
      editingKb.value = kb;
      kbForm.value = {
        name: kb.name
      };
      showCreateDialog.value = true;
      break;
    case 'documents':
      currentKb.value = kb;
      showDocumentsDialog.value = true;
      loadDocuments();
      break;
    case 'delete':
      handleDeleteKb(kb);
      break;
  }
};

// 删除知识库
const handleDeleteKb = async (kb) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除知识库 "${kb.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    const token = await login();
    const response = await fetch('http://127.0.0.1/v1/kb/rm', {
      method: 'POST',
      headers: {
        'Authorization': token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        kb_id: kb.id
      })
    });
    
    if (!response.ok) {
      throw new Error('删除知识库失败');
    }
    
    ElMessage.success('知识库删除成功');
    await loadKnowledgeBases();
    // 刷新统计数据 - 添加安全检查
    if (statsRef.value && typeof statsRef.value.refreshStats === 'function') {
      statsRef.value.refreshStats();
    }
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.message || '删除知识库失败');
    }
  }
};

// 提交知识库表单
const submitKbForm = async () => {
  if (!kbFormRef.value) return;
  
  try {
    await kbFormRef.value.validate();
    submitting.value = true;
    
    const token = await login();
    
    if (editingKb.value) {
      // 更新知识库
      const updateData = {
        kb_id: editingKb.value.id,
        name: kbForm.value.name,
        avatar: "",
        description: null,
        permission: "me",
        parser_config: {
          layout_recognize: "DeepDOC",
          chunk_token_num: 512,
          delimiter: "\\n!?;。；！？",
          auto_keywords: 0,
          auto_questions: 0,
          html4excel: false,
          raptor: {
            use_raptor: false
          },
          graphrag: {
            use_graphrag: false
          }
        },
        embd_id: "bge-m3:latest@Ollama",
        parser_id: "naive",
        pagerank: 0
      };
      
      const response = await fetch('http://127.0.0.1/v1/kb/update', {
        method: 'POST',
        headers: {
          'Authorization': token,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
      });
      
      if (!response.ok) {
        throw new Error('更新知识库失败');
      }
      
      ElMessage.success('知识库更新成功');
    } else {
      // 创建知识库
      const createResponse = await fetch('http://127.0.0.1/v1/kb/create', {
        method: 'POST',
        headers: {
          'Authorization': token,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: kbForm.value.name
        })
      });
      
      if (!createResponse.ok) {
        throw new Error('创建知识库失败');
      }
      
      const createResult = await createResponse.json();
      if (createResult.code !== 0) {
        throw new Error(createResult.message || '创建知识库失败');
      }
      
      // 获取创建的知识库ID
      const kbId = createResult.data?.kb_id;
      if (!kbId) {
        throw new Error('创建知识库成功但未获取到ID');
      }
      
      // 创建成功后立即更新配置
      const updateData = {
        kb_id: kbId,
        name: kbForm.value.name,
        avatar: "",
        description: null,
        permission: "me",
        parser_config: {
          layout_recognize: "DeepDOC",
          chunk_token_num: 512,
          delimiter: "\\n!?;。；！？",
          auto_keywords: 0,
          auto_questions: 0,
          html4excel: false,
          raptor: {
            use_raptor: false
          },
          graphrag: {
            use_graphrag: false
          }
        },
        embd_id: "bge-m3:latest@Ollama",
        parser_id: "naive",
        pagerank: 0
      };
      
      const updateResponse = await fetch('http://127.0.0.1/v1/kb/update', {
        method: 'POST',
        headers: {
          'Authorization': token,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
      });
      
      if (!updateResponse.ok) {
        throw new Error('知识库配置更新失败');
      }
      
      const updateResult = await updateResponse.json();
      if (updateResult.code !== 0) {
        throw new Error(updateResult.message || '知识库配置更新失败');
      }
      
      ElMessage.success('知识库创建并配置成功');
    }
    
    showCreateDialog.value = false;
    await loadKnowledgeBases();
    // 刷新统计数据 - 添加安全检查
    if (statsRef.value && typeof statsRef.value.refreshStats === 'function') {
      statsRef.value.refreshStats();
    }
  } catch (err) {
    ElMessage.error(err.message || '操作失败');
  } finally {
    submitting.value = false;
  }
};

// 重置表单
const resetForm = () => {
  editingKb.value = null;
  kbForm.value = {
    name: ''
  };
  if (kbFormRef.value) {
    kbFormRef.value.resetFields();
  }
};

// 加载文档列表
const loadDocuments = async () => {
  if (!currentKb.value) return;
  
  documentsLoading.value = true;
  documentsError.value = '';
  
  try {
    const token = await login();
    const url = `http://127.0.0.1/v1/document/list?kb_id=${currentKb.value.id}&keywords=&page_size=10&page=1`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': token,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error('获取文档列表失败');
    }

    const data = await response.json();
    if (data.code === 0 && data.data && data.data.docs) {
      documents.value = data.data.docs;
    } else {
      documents.value = [];
    }
  } catch (err) {
    console.error('加载文档失败:', err);
    documentsError.value = err.message || '加载文档失败';
  } finally {
    documentsLoading.value = false;
  }
};

// 解析文档
const parseDocument = async (doc) => {
  try {
    // 设置解析状态
    doc.parsing = true;
    
    const token = await login();
    const response = await fetch('http://127.0.0.1/v1/document/run', {
      method: 'POST',
      headers: {
        'Authorization': token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        doc_ids: [doc.id],
        run: 1,
        delete: false
      })
    });

    if (!response.ok) {
      throw new Error('解析文档失败');
    }

    const result = await response.json();
    if (result.code === 0) {
      ElMessage.success('文档解析成功');
      // 刷新文档列表以获取最新状态
      await loadDocuments();
    } else {
      throw new Error(result.message || '解析文档失败');
    }
  } catch (err) {
    ElMessage.error(err.message || '解析文档失败');
  } finally {
    doc.parsing = false;
  }
};

// 删除文档
const deleteDocument = async (doc) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${doc.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    const token = await login();
    const response = await fetch('http://127.0.0.1/v1/document/rm', {
      method: 'POST',
      headers: {
        'Authorization': token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        doc_id: [doc.id]
      })
    });

    if (!response.ok) {
      throw new Error('删除文档失败');
    }

    ElMessage.success('文档删除成功');
    // 刷新知识库列表（更新文档总数）
    await loadKnowledgeBases();
    // 刷新文档列表
    await loadDocuments();
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.message || '删除文档失败');
    }
  }
};

// 重置文档表单
const resetDocumentForm = () => {
  currentKb.value = null;
  documents.value = [];
  documentsError.value = '';
};

// 上传相关方法
const uploadRef = ref();

const beforeUpload = (file) => {
  const isValidType = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'].includes(file.type);
  
  if (!isValidType) {
    ElMessage.error('只能上传 PDF、DOCX、TXT 格式的文件!');
    return false;
  }
  
  // 只验证文件类型，不阻止上传
  return true;
};

// 文件选择变化处理
const handleFileChange = (file, fileList) => {
  // 确保文件状态为 ready 时才添加到列表
  if (file.status === 'ready') {
    uploadFileList.value = [...fileList];
  }
};

// 文件移除处理
const handleFileRemove = (file, fileList) => {
  uploadFileList.value = [...fileList];
};





// 处理文件上传
const handleUploadFiles = async () => {
  if (!currentKb.value) {
    ElMessage.error('请先选择知识库');
    return;
  }
  
  if (uploadFileList.value.length === 0) {
    ElMessage.error('请先选择要上传的文件');
    return;
  }
  
  submitting.value = true;
  
  try {
    // 逐个上传文件
    for (let i = 0; i < uploadFileList.value.length; i++) {
      const file = uploadFileList.value[i];
      
      // 显示上传进度
      if (uploadFileList.value.length > 1) {
        ElMessage.info(`正在上传第 ${i + 1}/${uploadFileList.value.length} 个文件: ${file.name}`);
      }
      
      await uploadSingleFile(file);
    }
    
    // 所有文件上传完成
    ElMessage.success(`成功上传 ${uploadFileList.value.length} 个文档`);
    showUploadDialog.value = false;
    uploadFileList.value = [];
    
    // 刷新知识库列表（更新文档总数）
    await loadKnowledgeBases();
    // 刷新文档列表
    await loadDocuments();
    // 刷新统计数据
    if (statsRef.value && typeof statsRef.value.refreshStats === 'function') {
      statsRef.value.refreshStats();
    }
    
  } catch (err) {
    ElMessage.error(err.message || '文档上传失败');
  } finally {
    submitting.value = false;
  }
};

// 上传单个文件
const uploadSingleFile = async (file) => {
  const token = await login();
  const formData = new FormData();
  formData.append('file', file.raw);
  formData.append('kb_id', currentKb.value.id);
  
  const response = await fetch('http://127.0.0.1/v1/document/upload', {
    method: 'POST',
    headers: {
      'Authorization': token
    },
    body: formData
  });
  
  if (!response.ok) {
    throw new Error('上传失败');
  }
  
  const result = await response.json();
  if (result.code !== 0) {
    throw new Error(result.message || '上传失败');
  }
};

// 清空上传文件列表
const clearUploadFiles = () => {
  uploadFileList.value = [];
  if (uploadRef.value) {
    uploadRef.value.clearFiles();
  }
};

// 重置上传表单（与clearUploadFiles功能相同）
const resetUploadForm = clearUploadFiles;

// 工具函数
const formatDate = (timestamp) => {
  if (!timestamp) return '-';
  
  // 如果是时间戳（数字），需要转换为毫秒
  let date;
  if (typeof timestamp === 'number') {
    // 如果时间戳是秒级的，转换为毫秒
    if (timestamp < 1000000000000) {
      date = new Date(timestamp * 1000);
    } else {
      date = new Date(timestamp);
    }
  } else {
    date = new Date(timestamp);
  }
  
  if (isNaN(date.getTime())) {
    return '-';
  }
  return date.toLocaleString('zh-CN');
};

// 获取解析状态类型
const getParseStatusType = (doc) => {
  if (!doc) return 'info';
  
  // 根据run字段判断状态
  switch (doc.run) {
    case "0":
      return 'warning'; // 未解析
    case "1":
      return 'info'; // 解析中
    case "2":
      return 'info'; // 失败
    case "3":
      return 'success'; // 成功
    case "4":
      return 'danger'; // 失败
    default:
      return 'info';
  }
};

// 获取解析状态文本
const getParseStatusText = (doc) => {
  if (!doc) return '未知';
  
  // 根据run字段判断状态
  switch (doc.run) {
    case "0":
      return '未解析';
    case "1":
      return '解析中';
    case "2":
      return '未知';
    case "3":
      return '已解析';
    case "4":
      return '解析失败';
    default:
      return '未知';
  }
};

// 处理表格选择变化
const handleSelectionChange = (selection) => {
  selectedDocuments.value = selection;
};

// 清空选择
const clearSelection = () => {
  selectedDocuments.value = [];
  // 清空表格选择
  if (documentsTableRef.value) {
    documentsTableRef.value.clearSelection();
  }
};

// 批量解析文档
const batchParseDocuments = async () => {
  const parseableDocs = selectedDocuments.value.filter(doc => doc.run === '0' || doc.run === '2');
  
  if (parseableDocs.length === 0) {
    ElMessage.warning('没有可解析的文档');
    return;
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要解析选中的 ${parseableDocs.length} 个文档吗？`,
      '确认批量解析',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    );
    
    batchParsing.value = true;
    const docIds = parseableDocs.map(doc => doc.id);
    
    const token = await login();
    const response = await fetch('http://127.0.0.1/v1/document/run', {
      method: 'POST',
      headers: {
        'Authorization': token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        doc_ids: docIds,
        run: 1,
        delete: false
      })
    });
    
    if (!response.ok) {
      throw new Error('批量解析失败');
    }
    
    const result = await response.json();
    if (result.code === 0) {
      ElMessage.success(`成功启动 ${parseableDocs.length} 个文档的解析`);
      // 刷新文档列表
      await loadDocuments();
      // 清空选择
      clearSelection();
    } else {
      throw new Error(result.message || '批量解析失败');
    }
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.message || '批量解析失败');
    }
  } finally {
    batchParsing.value = false;
  }
};

// 批量删除文档
const batchDeleteDocuments = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedDocuments.value.length} 个文档吗？此操作不可恢复！`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    batchDeleting.value = true;
    const docIds = selectedDocuments.value.map(doc => doc.id);
    
    const token = await login();
    const response = await fetch('http://127.0.0.1/v1/document/rm', {
      method: 'POST',
      headers: {
        'Authorization': token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        doc_id: docIds
      })
    });
    
    if (!response.ok) {
      throw new Error('批量删除失败');
    }
    
    ElMessage.success(`成功删除 ${selectedDocuments.value.length} 个文档`);
    // 刷新知识库列表（更新文档总数）
    await loadKnowledgeBases();
    // 刷新文档列表
    await loadDocuments();
    // 清空选择
    clearSelection();
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.message || '批量删除失败');
    }
  } finally {
    batchDeleting.value = false;
  }
};

// 处理过滤结果
const handleFiltered = (filtered) => {
  filteredKnowledgeBases.value = filtered;
};

// 预览文档
const previewDocument = (doc) => {
  selectedFile.value = {
    id: doc.id,
    name: doc.name
  };
  filePreviewVisible.value = true;
};

// 关闭文件预览
const closeFilePreview = () => {
  filePreviewVisible.value = false;
  selectedFile.value = null;
};

// 获取文件类型
const getFileType = (fileName) => {
  if (!fileName) return '';
  const extension = fileName.split('.').pop().toLowerCase();
  return extension;
};

// 组件挂载时加载数据
onMounted(() => {
  loadKnowledgeBases();
});
</script>

<style scoped>
.knowledge-management-view {
  max-width: 1200px;
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

.actions-section {
  margin-bottom: 30px;
  display: flex;
  gap: 12px;
}

.kb-list-section {
  margin-bottom: 40px;
}

.loading-container, .error-container, .empty-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 60px 20px;
  color: #666;
  font-size: 1rem;
}

.error-container {
  color: #d93025;
}

.empty-container {
  color: #999;
}

.kb-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.kb-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.kb-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.kb-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kb-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #333;
}

.kb-content {
  padding: 0;
}

.kb-info {
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.info-item .label {
  color: #666;
  font-weight: 500;
}

.info-item .value {
  color: #333;
}



.documents-container {
  padding: 0;
}

.documents-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e8eaed;
}

.documents-header h4 {
  margin: 0;
  color: #333;
}

.documents-list {
  min-height: 200px;
}

@media (max-width: 768px) {
  .knowledge-management-view {
    padding: 16px;
  }
  
  .main-title {
    font-size: 1.8rem;
  }
  
  .kb-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-section {
    flex-direction: column;
  }
  
  .documents-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}

.upload-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* 批量操作样式 */
.batch-actions {
  margin-bottom: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 解析状态样式 */
.el-table .el-tag {
  font-size: 12px;
  padding: 2px 8px;
}

.el-table .el-button {
  margin-right: 8px;
}

.el-table .el-button:last-child {
  margin-right: 0;
}

/* 文档名称按钮样式 */
.document-name-button {
  color: #409EFF;
  font-weight: 500;
  padding: 0;
  height: auto;
  line-height: 1.4;
  text-decoration: none;
  transition: all 0.2s ease;
}

.document-name-button:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.document-name-button .el-icon {
  margin-right: 4px;
  font-size: 14px;
}
</style>