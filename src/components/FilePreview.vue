<template>
  <div class="file-preview-overlay" v-if="visible" @click="handleOverlayClick">
    <div class="file-preview-container" @click.stop>
      <div class="file-preview-header">
        <div class="file-preview-title">
          <el-icon><Document /></el-icon>
          <span>{{ fileName }}</span>
        </div>
        <div class="file-preview-actions">
          <el-button 
            type="text" 
            @click="handleDownload"
            :loading="downloading"
            size="small"
          >
            <el-icon><Download /></el-icon>
            下载
          </el-button>
          <el-button 
            type="text" 
            @click="closePreview"
            size="small"
          >
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </div>
      
      <div class="file-preview-content">
        <div v-if="loading" class="loading-container">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>正在加载文件...</span>
        </div>
        
        <div v-else-if="error" class="error-container">
          <el-icon><Warning /></el-icon>
          <span>{{ error }}</span>
        </div>
        
        <div v-else class="preview-container">
          <!-- Word文档预览 -->
          <VueOfficeDocx
            v-if="(fileType === 'docx' || fileType === 'doc') && fileContent"
            :src="fileContent"
            :width="previewWidth"
            :height="previewHeight"
            @rendered="onRendered"
            @error="onError"
          />
          
          <!-- PDF预览 -->
          <VueOfficePdf
            v-else-if="fileType === 'pdf' && fileContent"
            :src="fileContent"
            :width="previewWidth"
            :height="previewHeight"
            @rendered="onRendered"
            @error="onError"
          />
          
          <!-- 其他文件类型 -->
          <div v-else class="unsupported-file">
            <el-icon><Document /></el-icon>
            <p>不支持预览此文件类型: {{ fileType }}</p>
            <el-button type="primary" @click="handleDownload">下载文件</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue';
import { Document, Download, Close, Loading, Warning } from '@element-plus/icons-vue';
import VueOfficeDocx from '@vue-office/docx';
import VueOfficePdf from '@vue-office/pdf';
import '@vue-office/docx/lib/index.css';

export default {
  name: 'FilePreview',
  components: {
    Document,
    Download,
    Close,
    Loading,
    Warning,
    VueOfficeDocx,
    VueOfficePdf
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    docId: {
      type: String,
      default: ''
    },
    fileName: {
      type: String,
      default: ''
    },
    fileType: {
      type: String,
      default: ''
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const loading = ref(false);
    const downloading = ref(false);
    const error = ref('');
    const fileContent = ref('');
    const authToken = ref('');

    // 计算预览窗口尺寸
    const previewWidth = computed(() => window.innerWidth * 0.6);
    const previewHeight = computed(() => window.innerHeight * 1.0);

    // 监听visible变化，当显示时加载文件
    watch(() => props.visible, async (newVal) => {
      if (newVal && props.docId) {
        console.log('FilePreview - 开始加载文件:', {
          docId: props.docId,
          fileName: props.fileName,
          fileType: props.fileType
        });
        await loadFile();
      } else {
        // 关闭时清理
        fileContent.value = '';
        error.value = '';
      }
    });

    // 登录获取token
    const login = async () => {
      try {
        const loginData = {
          email: '123@123.com',
          password: 'hXWqKtPnAt+tvQeaKHh87nNc5xbuVJu5thZtH1gBOzFfwmjml8DJp3/E2HzILWJVqWy3Vp79g3wPC67+ImkG1IQyvD4BSYXp4zlUy++toYQO1GOEMys4Xn8Xta2G9KTkjhWrR9qfOyEroIIzXEy2+HBf4DenGXPABLIh0HAGlZSdizpq3mHbIhHm26CDl0OIT7S7xd6YCOYpM9VC6IMYQI/a3r5qZc8cIvkQGrEnrhlPVIPQocxY5shmXwaEJxugPd/kezvsienh6TEfctqVcSwIssIgPBunOVJb2PDCF/NevwS3ZGqmFn7VIxUwHi0oz4KYZsudj+K8aJqG/8Jj8w=='
        };

        const response = await fetch('http://127.0.0.1/v1/user/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(loginData)
        });

        if (!response.ok) {
          throw new Error('登录失败');
        }

        const token = response.headers.get('Authorization');
        if (!token) {
          const body = await response.json();
          authToken.value = body.data?.access_token;
        } else {
          authToken.value = token;
        }

        if (!authToken.value) {
          throw new Error('未获取到token');
        }

        return authToken.value;
      } catch (err) {
        console.error('登录失败:', err);
        throw err;
      }
    };

    // 加载文件内容
    const loadFile = async () => {
      if (!props.docId) return;

      console.log('开始加载文件:', {
        docId: props.docId,
        fileName: props.fileName,
        fileType: props.fileType
      });

      loading.value = true;
      error.value = '';
      fileContent.value = '';

      try {
        // 确保已登录
        if (!authToken.value) {
          console.log('需要登录，开始登录...');
          await login();
        }

        console.log('发送文件请求:', `http://127.0.0.1/v1/document/get/${props.docId}`);

        // 获取文件内容
        const response = await fetch(`http://127.0.0.1/v1/document/get/${props.docId}`, {
          method: 'GET',
          headers: {
            'Authorization': authToken.value,
            'Content-Type': 'application/json'
          }
        });

        console.log('文件响应状态:', response.status);
        console.log('文件响应头:', Object.fromEntries(response.headers.entries()));

        if (!response.ok) {
          throw new Error(`文件加载失败: ${response.status}`);
        }

        // 检查响应的Content-Type
        const contentType = response.headers.get('content-type');
        console.log('响应Content-Type:', contentType);
        
        if (contentType && contentType.includes('application/json')) {
          console.log('处理JSON响应...');
          // 如果是JSON响应，按原来的方式处理
          try {
            const result = await response.json();
            console.log('JSON响应结果:', result);
            
            if (result.code === 0 && result.data?.content) {
              // 解码base64内容
              const base64Content = result.data.content;
              const binaryString = atob(base64Content);
              const bytes = new Uint8Array(binaryString.length);
              for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
              }
              
              // 创建Blob对象
              const blob = new Blob([bytes], { 
                type: getMimeType(props.fileType) 
              });
              
              // 创建URL
              fileContent.value = URL.createObjectURL(blob);
              console.log('从JSON创建文件URL成功');
            } else {
              throw new Error(result.message || '文件内容为空');
            }
          } catch (jsonError) {
            console.error('JSON解析失败，尝试作为文件内容处理:', jsonError);
            // JSON解析失败，尝试作为文件内容处理
            const fileBlob = await response.blob();
            fileContent.value = URL.createObjectURL(fileBlob);
            console.log('从Blob创建文件URL成功');
          }
        } else {
          console.log('处理直接文件内容...');
          // 如果直接返回文件内容，直接处理
          const fileBlob = await response.blob();
          
          // 创建URL
          fileContent.value = URL.createObjectURL(fileBlob);
          console.log('从直接文件内容创建URL成功');
        }
      } catch (err) {
        console.error('加载文件失败:', err);
        error.value = err.message || '加载文件失败';
      } finally {
        loading.value = false;
      }
    };

    // 获取MIME类型
    const getMimeType = (fileType) => {
      const mimeTypes = {
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'doc': 'application/msword',
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'rtf': 'application/rtf',
        'odt': 'application/vnd.oasis.opendocument.text'
      };
      return mimeTypes[fileType.toLowerCase()] || 'application/octet-stream';
    };

    // 下载文件
    const handleDownload = async () => {
      if (!fileContent.value) return;

      downloading.value = true;
      try {
        const response = await fetch(fileContent.value);
        const blob = await response.blob();
        
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = props.fileName || 'document';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (err) {
        console.error('下载失败:', err);
        error.value = '下载失败';
      } finally {
        downloading.value = false;
      }
    };

    // 关闭预览
    const closePreview = () => {
      if (fileContent.value) {
        URL.revokeObjectURL(fileContent.value);
      }
      emit('close');
    };

    // 点击遮罩层关闭
    const handleOverlayClick = () => {
      closePreview();
    };

    // 渲染完成回调
    const onRendered = () => {
      console.log('文件渲染完成');
    };

    // 渲染错误回调
    const onError = (err) => {
      console.error('文件渲染失败:', err);
      error.value = '文件渲染失败';
    };

    return {
      loading,
      downloading,
      error,
      fileContent,
      previewWidth,
      previewHeight,
      handleDownload,
      closePreview,
      handleOverlayClick,
      onRendered,
      onError
    };
  }
};
</script>

<style scoped>
.file-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999999;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  animation: fadeIn 0.3s ease;
}

.file-preview-container {
  width: 60%;
  height: 100%;
  background-color: white;
  border-radius: 8px 0 0 8px;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s ease;
}

.file-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #f8f9fa;
  border-radius: 8px 0 0 0;
}

.file-preview-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.file-preview-actions {
  display: flex;
  gap: 8px;
}

.file-preview-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  color: #909399;
}

.loading-container .el-icon {
  font-size: 32px;
  color: #409EFF;
}

.error-container .el-icon {
  font-size: 32px;
  color: #f56c6c;
}

.preview-container {
  height: 100%;
  overflow: auto;
}

.unsupported-file {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  color: #909399;
}

.unsupported-file .el-icon {
  font-size: 48px;
  color: #c0c4cc;
}

.unsupported-file p {
  margin: 0;
  font-size: 16px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .file-preview-container {
    width: 100%;
    height: 100%;
    border-radius: 0;
  }
  
  .file-preview-header {
    border-radius: 0;
  }
}
</style> 