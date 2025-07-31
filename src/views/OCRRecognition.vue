<template>
  <div class="ocr-recognition-view">
    <!-- 文件上传区域 -->
    <div class="upload-section">
      <div class="upload-container">
        <div class="upload-header">
          <h1>OCR文字识别</h1>
          <p>支持图片和PDF文件的文字识别，快速提取文档内容</p>
        </div>

        <div class="upload-content">
          <div class="upload-area">
            <el-upload
              v-model:file-list="fileList"
              class="upload-dragger"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              accept=".jpg,.jpeg,.png,.pdf"
              :limit="1"
              :show-file-list="false"
            >
              <div class="upload-inner">
                <el-icon class="upload-icon"><UploadFilled /></el-icon>
                <div class="upload-text">
                  <h3>点击或拖拽文件到此区域</h3>
                  <p>支持 JPG、PNG、PDF 格式，单个文件最大 10MB</p>
                </div>
              </div>
            </el-upload>

            <!-- 文件信息 -->
            <div v-if="fileList.length > 0" class="file-info">
              <div class="file-card">
                <div class="file-header">
                  <div class="file-basic-info">
                    <el-icon class="file-type-icon">
                      <Document v-if="fileList[0].raw?.type === 'application/pdf'" />
                      <Picture v-else />
                    </el-icon>
                    <div class="file-details">
                      <h4>{{ fileList[0].name }}</h4>
                      <p>{{ formatFileSize(fileList[0].size || fileList[0].raw?.size) }}</p>
                    </div>
                  </div>
                  <el-button size="small" type="danger" @click="clearFile" circle>
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 控制区域 -->
          <div class="control-area">
            <div class="settings-card">
              <h4>识别设置</h4>
              <div class="setting-item">
                <label>可视化结果</label>
                <el-switch v-model="ocrSettings.visualize" />
              </div>
            </div>

            <div class="action-buttons">
              <el-button
                type="primary"
                size="large"
                :loading="isProcessing"
                :disabled="fileList.length === 0"
                @click="startOCR"
                class="primary-action"
              >
                <el-icon v-if="!isProcessing"><DocumentChecked /></el-icon>
                {{ isProcessing ? '识别中...' : '开始识别' }}
              </el-button>

              <el-button
                size="large"
                @click="clearAll"
                :disabled="isProcessing"
                class="secondary-action"
              >
                <el-icon><Delete /></el-icon>
                清空重置
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 识别结果区域 -->
    <div class="results-section" v-if="isProcessing || ocrResults.length > 0">
      <div class="results-container">
        <div class="results-header">
          <h2>识别结果</h2>
          <div class="results-actions" v-if="ocrResults.length > 0">
            <el-button @click="copyAllText">
              <el-icon><DocumentCopy /></el-icon>
              复制全部文字
            </el-button>
            <el-button @click="downloadResults">
              <el-icon><Download /></el-icon>
              下载结果
            </el-button>
          </div>
        </div>

        <!-- 处理中状态 -->
        <div v-if="isProcessing" class="processing-card">
          <div class="processing-content">
            <div class="processing-animation">
              <el-icon class="rotating"><Loading /></el-icon>
            </div>
            <h3>正在识别中...</h3>
            <p>{{ processingStatus }}</p>
          </div>
        </div>

        <!-- 结果展示 - 分页形式 -->
        <div v-else class="results-content">
          <div v-if="ocrResults.length > 0" class="pagination-results">
            <!-- 分页控制器 -->
            <div class="pagination-controls">
              <div class="page-info">
                <span>第 {{ currentPage + 1 }} 页，共 {{ ocrResults.length }} 页</span>
              </div>
              <div class="page-buttons">
                <el-button
                  :disabled="currentPage === 0"
                  @click="previousPage"
                  circle
                >
                  <el-icon><ArrowLeft /></el-icon>
                </el-button>
                <el-button
                  :disabled="currentPage === ocrResults.length - 1"
                  @click="nextPage"
                  circle
                >
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>

            <!-- 当前页结果 -->
            <div class="current-page-result">
              <div class="result-item">
                <div class="result-header">
                  <h3>第 {{ currentPage + 1 }} 页识别结果</h3>
                  <!-- <div class="result-stats">
                    <el-tag type="info">{{ currentResult.wordCount }} 字</el-tag>
                    <el-tag type="success" v-if="currentResult.confidence">
                      置信度: {{ (currentResult.confidence * 100).toFixed(1) }}%
                    </el-tag>
                  </div> -->
                </div>

                <div class="result-content">
                  <!-- 图像展示区域 -->
                  <div class="images-area" v-if="currentResult.images">
                    <div class="image-card" v-if="currentResult.images.input">
                      <div class="image-header">
                        <h4>原始图像</h4>
                        <el-button size="small" @click="viewFullImage(currentResult.images.input, '原始图像')">
                          <el-icon><ZoomIn /></el-icon>
                          查看大图
                        </el-button>
                      </div>
                      <div class="image-container">
                        <img
                          :src="'data:image/jpeg;base64,' + currentResult.images.input"
                          alt="原始图像"
                          @click="viewFullImage(currentResult.images.input, '原始图像')"
                        />
                      </div>
                    </div>

                    <div class="image-card" v-if="currentResult.images.ocr">
                      <div class="image-header">
                        <h4>OCR识别可视化</h4>
                        <el-button size="small" @click="viewFullImage(currentResult.images.ocr, 'OCR识别可视化')">
                          <el-icon><ZoomIn /></el-icon>
                          查看大图
                        </el-button>
                      </div>
                      <div class="image-container">
                        <img
                          :src="'data:image/jpeg;base64,' + currentResult.images.ocr"
                          alt="OCR可视化"
                          @click="viewFullImage(currentResult.images.ocr, 'OCR识别可视化')"
                        />
                      </div>
                    </div>

                    <div class="image-card" v-if="currentResult.images.preprocessing">
                      <div class="image-header">
                        <h4>文档预处理</h4>
                        <el-button size="small" @click="viewFullImage(currentResult.images.preprocessing, '文档预处理')">
                          <el-icon><ZoomIn /></el-icon>
                          查看大图
                        </el-button>
                      </div>
                      <div class="image-container">
                        <img
                          :src="'data:image/jpeg;base64,' + currentResult.images.preprocessing"
                          alt="文档预处理"
                          @click="viewFullImage(currentResult.images.preprocessing, '文档预处理')"
                        />
                      </div>
                    </div>
                  </div>

                  <!-- 文字内容 -->
                  <div class="text-area">
                    <div class="text-card">
                      <div class="text-header">
                        <h4>识别文字内容</h4>
                        <el-button size="small" @click="copyPageText(currentResult.text)">
                          <el-icon><DocumentCopy /></el-icon>
                          复制文字
                        </el-button>
                      </div>
                      <div class="text-content">
                        {{ currentResult.text || '暂无识别到文字内容' }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图像查看对话框 -->
    <el-dialog v-model="imageViewDialogVisible" :title="imageViewTitle" width="80%" class="image-view-dialog">
      <div class="image-view-content">
        <img
          v-if="currentViewImage"
          :src="'data:image/jpeg;base64,' + currentViewImage"
          alt="图像查看"
          class="full-image"
        />
      </div>
      <template #footer>
        <el-button @click="imageViewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="downloadImage">下载图像</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import {
  UploadFilled,
  Document,
  Picture,
  Delete,
  DocumentChecked,
  Download,
  DocumentCopy,
  Loading,
  ZoomIn,
  ArrowLeft,
  ArrowRight
} from '@element-plus/icons-vue';

// API配置
const API_URL = "http://124.16.71.198:5678/ocr";

// 状态变量
const fileList = ref([]);
const ocrSettings = ref({
  visualize: true
});
const isProcessing = ref(false);
const processingStatus = ref('');
const ocrResults = ref([]);

// 分页相关变量
const currentPage = ref(0);

// 图像查看相关变量
const imageViewDialogVisible = ref(false);
const currentViewImage = ref('');
const imageViewTitle = ref('');

// 计算属性：当前页结果
const currentResult = computed(() => {
  if (ocrResults.value.length > 0 && currentPage.value < ocrResults.value.length) {
    return ocrResults.value[currentPage.value];
  }
  return {
    text: '',
    wordCount: 0,
    confidence: 0,
    images: {}
  };
});

// 文件处理函数
const handleFileChange = (uploadFile, fileListParam) => {
  if (fileListParam.length > 1) {
    fileListParam.splice(1); // 只保留第一个
  }
};

const handleFileRemove = () => {
  fileList.value = [];
};

const clearFile = () => {
  fileList.value = [];
};

const clearAll = () => {
  fileList.value = [];
  ocrResults.value = [];
  isProcessing.value = false;
  processingStatus.value = '';
  currentPage.value = 0;
};

// 分页函数
const previousPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--;
  }
};

const nextPage = () => {
  if (currentPage.value < ocrResults.value.length - 1) {
    currentPage.value++;
  }
};

// 格式化文件大小
const formatFileSize = (size) => {
  if (!size) return '0 B';
  if (size < 1024) return size + ' B';
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB';
  if (size < 1024 * 1024 * 1024) return (size / (1024 * 1024)).toFixed(2) + ' MB';
  return (size / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
};

// 文件转Base64
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = err => reject(err);
  });
};

// OCR识别函数
const startOCR = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先上传文件');
    return;
  }

  isProcessing.value = true;
  processingStatus.value = '正在准备文件...';
  ocrResults.value = [];

  try {
    const file = fileList.value[0].raw;
    processingStatus.value = '正在转换文件格式...';

    const base64 = await fileToBase64(file);

    const payload = {
      file: base64,
      fileType: file.type === 'application/pdf' ? 0 : 1,
      visualize: ocrSettings.value.visualize
    };

    processingStatus.value = '正在发送请求...';

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    processingStatus.value = '正在解析结果...';
    const result = await response.json();

    // 打印完整的响应数据用于调试
    console.log('服务器返回的完整数据:', JSON.stringify(result, null, 2));

    // 处理OCR结果 - 根据实际的响应结构调整
    let processedResults = [];

    // 检查不同可能的数据结构
    if (result && result.result && result.result.ocrResults) {
      // 如果数据在 result.result.ocrResults 中
      const ocrData = result.result.ocrResults;
      console.log('找到 result.result.ocrResults:', ocrData);

      // 检查是否是数组
      const resultsArray = Array.isArray(ocrData) ? ocrData : Object.values(ocrData);

      for (let i = 0; i < resultsArray.length; i++) {
        const pageResult = resultsArray[i];
        console.log(`处理第 ${i + 1} 页数据:`, pageResult);

        const pageData = {
          pageNumber: i + 1,
          text: '',
          wordCount: 0,
          confidence: 0,
          images: {
            input: pageResult.inputImage || null,
            ocr: pageResult.ocrImage || null,
            preprocessing: pageResult.docPreprocessingImage || null
          }
        };

        // 从prunedResult中提取文本内容
        if (pageResult.prunedResult && pageResult.prunedResult.rec_texts) {
          const texts = pageResult.prunedResult.rec_texts.filter(text => text && text.trim());
          pageData.text = texts.join('\n');
          pageData.wordCount = texts.length;

          // 计算平均置信度
          if (pageResult.prunedResult.rec_scores && pageResult.prunedResult.rec_scores.length > 0) {
            const totalConfidence = pageResult.prunedResult.rec_scores.reduce((sum, score) => sum + score, 0);
            pageData.confidence = totalConfidence / pageResult.prunedResult.rec_scores.length;
          }
        }

        processedResults.push(pageData);
      }
    } else if (result && result.ocrResults) {
      // 如果数据直接在 result.ocrResults 中
      const ocrData = result.ocrResults;
      console.log('找到 result.ocrResults:', ocrData);

      const resultsArray = Array.isArray(ocrData) ? ocrData : Object.values(ocrData);

      for (let i = 0; i < resultsArray.length; i++) {
        const pageResult = resultsArray[i];

        const pageData = {
          pageNumber: i + 1,
          text: '',
          wordCount: 0,
          confidence: 0,
          images: {
            input: pageResult.inputImage || null,
            ocr: pageResult.ocrImage || null,
            preprocessing: pageResult.docPreprocessingImage || null
          }
        };

        if (pageResult.prunedResult && pageResult.prunedResult.rec_texts) {
          const texts = pageResult.prunedResult.rec_texts.filter(text => text && text.trim());
          pageData.text = texts.join('\n');
          pageData.wordCount = texts.length;

          if (pageResult.prunedResult.rec_scores && pageResult.prunedResult.rec_scores.length > 0) {
            const totalConfidence = pageResult.prunedResult.rec_scores.reduce((sum, score) => sum + score, 0);
            pageData.confidence = totalConfidence / pageResult.prunedResult.rec_scores.length;
          }
        }

        processedResults.push(pageData);
      }
    } else {
      // 如果找不到预期的数据结构，显示详细错误信息
      console.error('无法找到OCR结果数据，响应结构:', Object.keys(result));
      throw new Error(`服务器返回的数据格式不正确。响应包含的字段: ${Object.keys(result).join(', ')}`);
    }

    if (processedResults.length > 0) {
      ocrResults.value = processedResults;
      currentPage.value = 0; // 重置到第一页
      ElMessage.success(`识别完成！共识别 ${processedResults.length} 页内容`);
    } else {
      throw new Error('未能从响应中提取到任何OCR结果');
    }

  } catch (error) {
    console.error('OCR识别失败:', error);
    ElMessage.error('OCR识别失败: ' + error.message);
  } finally {
    isProcessing.value = false;
    processingStatus.value = '';
  }
};

// 复制文字功能
const copyPageText = async (text) => {
  try {
    await navigator.clipboard.writeText(text || '');
    ElMessage.success('文字已复制到剪贴板');
  } catch (error) {
    ElMessage.error('复制失败，请手动复制');
  }
};

const copyAllText = async () => {
  try {
    const allText = ocrResults.value.map((result, index) => {
      return `=== 第 ${index + 1} 页 ===\n${result.text || ''}`;
    }).join('\n\n');

    await navigator.clipboard.writeText(allText);
    ElMessage.success('全部文字已复制到剪贴板');
  } catch (error) {
    ElMessage.error('复制失败，请手动复制');
  }
};

// 查看全尺寸图像
const viewFullImage = (imageData, title) => {
  currentViewImage.value = imageData;
  imageViewTitle.value = title;
  imageViewDialogVisible.value = true;
};

// 下载图像
const downloadImage = () => {
  if (currentViewImage.value) {
    const link = document.createElement('a');
    link.href = 'data:image/jpeg;base64,' + currentViewImage.value;
    link.download = `${imageViewTitle.value}.jpg`;
    link.click();
  }
};

// 下载结果
const downloadResults = () => {
  const allText = ocrResults.value.map((result, index) => {
    return `=== 第 ${index + 1} 页 ===\n${result.text || ''}`;
  }).join('\n\n');

  const blob = new Blob([allText], { type: 'text/plain;charset=utf-8' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `OCR识别结果_${new Date().toISOString().slice(0, 10)}.txt`;
  link.click();
  URL.revokeObjectURL(link.href);

  ElMessage.success('结果已下载');
};
</script>

<style scoped>
.ocr-recognition-view {
  min-height: 100vh;
  background: #ffffff;
}

/* 上传区域样式 */
.upload-section {
  padding: 40px 20px;
  background: #ffffff;
}

.upload-container {
  max-width: 1200px;
  margin: 0 auto;
}

.upload-header {
  text-align: center;
  margin-bottom: 40px;
  color: #333333;
}

.upload-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 16px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.upload-header p {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0;
}

.upload-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.upload-area {
  margin-bottom: 30px;
}

.upload-dragger {
  width: 100%;
}

.upload-dragger :deep(.el-upload-dragger) {
  width: 100%;
  height: 200px;
  border: 2px dashed #d9d9d9;
  border-radius: 16px;
  background: #fafafa;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-dragger :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: #f0f9ff;
}

.upload-inner {
  text-align: center;
}

.upload-icon {
  font-size: 4rem;
  color: #409eff;
  margin-bottom: 16px;
}

.upload-text h3 {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 8px;
}

.upload-text p {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

/* 文件信息卡片 */
.file-info {
  margin-top: 20px;
}

.file-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.file-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.file-basic-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.file-type-icon {
  font-size: 2rem;
  color: #409eff;
}

.file-details h4 {
  margin: 0 0 4px 0;
  font-size: 1rem;
  color: #333;
}

.file-details p {
  margin: 0;
  font-size: 0.9rem;
  color: #666;
}

/* 控制区域 */
.control-area {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 30px;
  align-items: end;
}

.settings-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.settings-card h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 1rem;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.setting-item label {
  color: #666;
  font-size: 0.9rem;
}

.action-buttons {
  display: flex;
  gap: 16px;
}

.primary-action {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 600;
}

.secondary-action {
  border-radius: 12px;
  padding: 12px 24px;
}

/* 结果区域样式 */
.results-section {
  background: #f8fafc;
  min-height: 60vh;
  padding: 40px 20px;
}

.results-container {
  max-width: 1200px;
  margin: 0 auto;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
}

.results-header h2 {
  color: #333;
  font-size: 1.8rem;
  margin: 0;
}

.results-actions {
  display: flex;
  gap: 12px;
}

/* 处理中状态 */
.processing-card {
  background: white;
  border-radius: 16px;
  padding: 60px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.processing-animation {
  margin-bottom: 24px;
}

.rotating {
  font-size: 3rem;
  color: #409eff;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.processing-content h3 {
  color: #333;
  margin: 0 0 12px 0;
  font-size: 1.4rem;
}

.processing-content p {
  color: #666;
  margin: 0;
  font-size: 1rem;
}

/* 结果内容 */
.results-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 分页结果样式 */
.pagination-results {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  border-radius: 12px;
  padding: 20px 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.page-info {
  font-size: 1rem;
  color: #374151;
  font-weight: 500;
}

.page-buttons {
  display: flex;
  gap: 12px;
}

.page-buttons .el-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.current-page-result {
  width: 100%;
}

.result-item {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.result-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.result-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.result-stats {
  display: flex;
  gap: 12px;
}

.result-content {
  padding: 30px;
}

/* 图像展示区域 */
.images-area {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.image-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.image-header {
  background: #f9fafb;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e5e7eb;
}

.image-header h4 {
  margin: 0;
  font-size: 1rem;
  color: #374151;
}

.image-container {
  padding: 16px;
  text-align: center;
}

.image-container img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.image-container img:hover {
  transform: scale(1.02);
}

/* 文字内容区域 */
.text-area {
  margin-top: 20px;
}

.text-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.text-header {
  background: #f9fafb;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e5e7eb;
}

.text-header h4 {
  margin: 0;
  font-size: 1rem;
  color: #374151;
}

.text-content {
  padding: 20px;
  background: white;
  font-family: 'Courier New', monospace;
  line-height: 1.6;
  color: #374151;
  white-space: pre-wrap;
  word-break: break-word;
  min-height: 120px;
  max-height: 400px;
  overflow-y: auto;
}

/* 图像查看对话框 */
.image-view-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.image-view-content {
  text-align: center;
  background: #f5f5f5;
  padding: 20px;
}

.full-image {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-header h1 {
    font-size: 2rem;
  }

  .upload-content {
    padding: 20px;
  }

  .control-area {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .action-buttons {
    justify-content: center;
  }

  .results-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .results-actions {
    justify-content: center;
  }

  .images-area {
    grid-template-columns: 1fr;
  }

  .result-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .result-stats {
    justify-content: center;
  }
}
</style>