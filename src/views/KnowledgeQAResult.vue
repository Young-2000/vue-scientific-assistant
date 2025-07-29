<template>
  <div class="knowledge-qa-result-view">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
      <div class="decoration-circle circle-3"></div>
    </div>

    <div class="content-container">
      <div class="header">
        <div class="header-content">
          <div class="title-section">
            <div class="icon-wrapper">
              <el-icon class="title-icon"><Search /></el-icon>
            </div>
            <h2 class="main-title">知识库问答结果</h2>
          </div>
          <div class="header-subtitle">基于您的知识库提供精准答案</div>
        </div>
      </div>

      <!-- 搜索问题显示 -->
      <div class="question-section">
        <div class="question-container">
          <div class="question-header">
            <el-icon class="question-icon"><ChatDotRound /></el-icon>
            <h3>您的问题</h3>
          </div>
          <div class="question-text">{{ question }}</div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-section">
        <div class="loading-card">
          <div class="loading-content">
            <div class="loading-spinner">
              <div class="spinner-ring"></div>
              <div class="spinner-ring"></div>
              <div class="spinner-ring"></div>
            </div>
            <h3>正在搜索知识库</h3>
            <p>AI正在为您分析问题并检索相关信息...</p>
            <div class="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜索结果区域 -->
      <div v-else-if="hasResults" class="results-section">
        <!-- 主要回答 -->
        <div class="main-answer" v-if="mainAnswer">
          <div class="answer-header">
            <div class="answer-icon-wrapper">
              <el-icon class="answer-icon"><Light /></el-icon>
            </div>
            <h3>AI 回答</h3>
          </div>
          <div class="answer-content markdown-body" v-html="renderMarkdown(mainAnswer)"></div>
        </div>

        <!-- 相关文档 -->
        <div class="related-docs" v-if="relatedDocs.length > 0">
          <div class="section-header">
            <div class="section-icon-wrapper">
              <el-icon class="section-icon"><Document /></el-icon>
            </div>
            <h3>相关文档</h3>
            <span class="doc-count">{{ relatedDocs.length }} 个文档</span>
          </div>
          <div class="docs-list">
            <div 
              v-for="(doc, index) in relatedDocs" 
              :key="index"
              class="doc-item"
              :class="{ 'doc-item-hover': doc.isHovered }"
              @click="showDocReference(doc, $event)"
              @mouseenter="doc.isHovered = true"
              @mouseleave="doc.isHovered = false"
            >
              <div class="doc-header">
                <div class="doc-title">{{ doc.doc_name || '未知文档' }}</div>
                <div class="doc-index">#{{ index + 1 }}</div>
              </div>
              <div class="doc-content" v-if="doc.content" v-html="doc.content"></div>
              <div class="doc-footer">
                <el-icon class="doc-footer-icon"><View /></el-icon>
                <span>点击查看详情</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 相关问题 -->
        <div class="related-questions" v-if="relatedQuestions.length > 0">
          <div class="section-header">
            <div class="section-icon-wrapper">
              <el-icon class="section-icon"><QuestionFilled /></el-icon>
            </div>
            <h3>相关问题</h3>
            <span class="question-count">{{ relatedQuestions.length }} 个问题</span>
          </div>
          <div class="questions-list">
            <el-button
              v-for="(question, index) in relatedQuestions"
              :key="index"
              class="question-item"
              @click="selectQuestion(question)"
            >
              <el-icon class="question-item-icon"><ArrowRight /></el-icon>
              {{ question }}
            </el-button>
          </div>
        </div>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="hasError" class="error-section">
        <div class="error-card">
          <div class="error-content">
            <div class="error-icon-wrapper">
              <el-icon class="error-icon"><Warning /></el-icon>
            </div>
            <h3>搜索失败</h3>
            <p class="error-message">{{ errorMessage }}</p>
            
            <!-- 根据错误类型显示不同的解决建议 -->
            <div class="error-suggestions" v-if="errorMessage">
              <h4>可能的解决方案：</h4>
              <ul v-if="errorMessage.includes('网络连接失败')">
                <li>检查网络连接是否正常</li>
                <li>尝试刷新页面</li>
                <li>检查防火墙设置</li>
              </ul>
              <ul v-else-if="errorMessage.includes('认证失败')">
                <li>系统正在自动重新登录</li>
                <li>如果问题持续，请刷新页面</li>
              </ul>
              <ul v-else-if="errorMessage.includes('服务器内部错误')">
                <li>服务器暂时不可用，请稍后重试</li>
                <li>如果问题持续，请联系管理员</li>
              </ul>
              <ul v-else-if="errorMessage.includes('请求超时')">
                <li>网络响应较慢，请稍后重试</li>
                <li>尝试简化问题内容</li>
              </ul>
              <ul v-else-if="errorMessage.includes('知识库')">
                <li>检查知识库是否存在</li>
                <li>确认知识库权限设置</li>
                <li>尝试重新选择知识库</li>
              </ul>
              <ul v-else>
                <li>请稍后重试</li>
                <li>如果问题持续，请联系技术支持</li>
              </ul>
            </div>
            
            <div class="error-actions">
              <el-button type="primary" class="retry-button" @click="retrySearch">
                <el-icon class="retry-icon"><Refresh /></el-icon>
                重试搜索
              </el-button>
              <el-button @click="goBack" class="back-button">
                <el-icon><ArrowLeft /></el-icon>
                返回搜索
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 引用弹出组件 -->
    <ReferenceDisplay 
      v-if="referencePopup.visible"
      :references="referencePopup.displayReferences"
      :visible="referencePopup.visible"
      :position="referencePopup.position"
      :files="referencePopup.files"
      @close="closeReferencePopup"
      @file-click="handleFileClick"
    />
    
    <!-- 文件预览组件 - 最高层级 -->
    <FilePreview
      :visible="filePreviewVisible"
      :doc-id="selectedFile?.doc_id"
      :file-name="selectedFile?.doc_name"
      :file-type="getFileType(selectedFile?.doc_name)"
      @close="closeFilePreview"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { 
  Warning, 
  Search, 
  ChatDotRound, 
  Light, 
  Document, 
  QuestionFilled, 
  View, 
  ArrowRight, 
  ArrowLeft,
  Refresh
} from '@element-plus/icons-vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import ReferenceDisplay from '@/components/ReferenceDisplay.vue';
import FilePreview from '@/components/FilePreview.vue';

// 定义props
const props = defineProps({
  question: {
    type: String,
    default: ''
  }
});

const router = useRouter();
const route = useRoute();

// 从props或路由query参数获取问题
const question = ref(props.question || route.query.question || '');

// 响应式数据
const isLoading = ref(true);
const hasResults = ref(false);
const hasError = ref(false);
const errorMessage = ref('');
const mainAnswer = ref('');
const relatedDocs = ref([]);
const relatedQuestions = ref([]);
const referencePopup = ref({
  visible: false,
  references: [], // 存储所有引用数据
  displayReferences: [], // 存储当前显示的引用数据
  position: { x: 0, y: 0 },
  files: [] // 新增：存储文件引用
});

// API相关
const authToken = ref('');
const headers = ref({});
const kb_ids = ref([]);
const controller = ref(null);

// 文件预览相关
const filePreviewVisible = ref(false);
const selectedFile = ref(null);

// 登录函数
const login = async () => {
  try {
    const loginData = {
      email: '123@123.com',
      password: "FN6pAfTq1saZeM+LtMwzA1Ao9fIQRct9OcVeJjhWul6Y+ki/Uzb4X6tvI1T591CFP2HmK6M4ZYbpT1OZM3rv9tvAE4c7S9nnXZ+ffg6w2Rq9OgOLCCbk5T7rapP6UxWD14aM62zbo1WtzSRKlC87Ik17U9UzPFlXbvdIEAzQr06GgRADmpvw3Msk05CvZTy9/f26q5TxlQOREFhZglTFTirosHdg09wnnA+f6CkZgm7Vvza+0ZJcRONmXUN8NFkY0rYxBJhaLUJQclFcGVjplVPbCQeSOafXI1yv3JN2NoV1e1s2A3LNdg0jxh6oEQ0TrveMyQfhytxNQqAGoT8lgg=="
      };

    console.log('发送登录请求的payload:', loginData);

    const response = await fetch('http://127.0.0.1/v1/user/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(loginData)
    });

    console.log('登录响应状态码:', response.status);
    console.log('登录请求的响应:', response.headers);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('登录失败，响应内容:', errorText);
      
      let errorMessage = '登录失败';
      if (response.status === 401) {
        errorMessage = '用户名或密码错误';
      } else if (response.status === 500) {
        errorMessage = '服务器内部错误';
      } else if (response.status === 503) {
        errorMessage = '服务暂时不可用';
      } else if (response.status === 400) {
        errorMessage = '登录参数错误';
      }
      
      throw new Error(`${errorMessage} (状态码: ${response.status})`);
    }

    const token = response.headers.get('Authorization');
    console.log('登录返回的token:', token);
    
    if (token) {
      authToken.value = token;
      headers.value = {
        "Authorization": token,
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json",
      };
      console.log('设置请求头:', headers.value);
    } else {
      throw new Error('登录成功但未获取到token');
    }

    // 获取知识库列表
    console.log('开始获取知识库列表...');
    const kbResponse = await fetch('http://127.0.0.1/v1/kb/list', {
      method: 'GET',
      headers: headers.value,
    });

    console.log('知识库列表响应状态码:', kbResponse.status);

    if (!kbResponse.ok) {
      const errorText = await kbResponse.text();
      console.error('获取知识库列表失败，响应内容:', errorText);
      
      let errorMessage = '获取知识库列表失败';
      if (kbResponse.status === 401) {
        errorMessage = '认证失败，请重新登录';
      } else if (kbResponse.status === 500) {
        errorMessage = '服务器内部错误';
      } else if (kbResponse.status === 404) {
        errorMessage = '知识库服务不可用';
      } else if (kbResponse.status === 403) {
        errorMessage = '没有权限访问知识库';
      }
      
      throw new Error(`${errorMessage} (状态码: ${kbResponse.status})`);
    }

    const kbData = await kbResponse.json();
    console.log('知识库列表返回的完整结果:', kbData);
    
    if (kbData.code === 0 && kbData.data) {
      const kbList = kbData.data.kbs || [];
      console.log('原始知识库列表:', kbList);
      
      kb_ids.value = kbList
        .filter(kb => kb.id)
        .map(kb => kb.id);
      console.log('提取的知识库ID列表:', kb_ids.value);
    } else {
      console.error('知识库列表响应格式错误:', kbData);
      throw new Error('知识库列表响应格式错误');
    }

  } catch (error) {
    console.error('登录失败:', error);
    throw error;
  }
};

// 执行搜索
const performSearch = async () => {
  isLoading.value = true;
  hasResults.value = false;
  hasError.value = false;
  mainAnswer.value = '';
  relatedDocs.value = [];
  relatedQuestions.value = [];

  // 使用选中的知识库
  if (kb_ids.value.length === 0) {
    hasError.value = true;
    errorMessage.value = '请先选择一个知识库。';
    isLoading.value = false;
    return;
  }

  // 三个请求并行发出
  const askPromise = sendAskStream();
  const retrievalPromise = getRetrievalTest();
  const relatedPromise = getRelatedQuestions();

  // 等ask结束
  await askPromise;

  // 等retrieval和related都结束
  await Promise.all([retrievalPromise, relatedPromise]);

  // 统一展示
  hasResults.value = true;
  isLoading.value = false;
};

// 重试搜索
const retrySearch = () => {
  performSearch();
};

// 返回搜索页面
const goBack = () => {
  router.push('/knowledge-qa');
};

// 发送ask流式请求
const sendAskStream = async () => {
  if (!question.value.trim()) return;

  const userMessageContent = question.value;
  
  // 取消之前的请求
  if (controller.value) {
    controller.value.abort();
  }
  controller.value = new AbortController();
  
  try {
    // 添加加载中的消息
    isLoading.value = true;
    mainAnswer.value = '正在生成中...';
    hasResults.value = true;
    hasError.value = false;

    console.log('\n=== 调用 /v1/conversation/ask 接口 ===');
    const askData = {
      question: userMessageContent,
      conversation_id: "",
      user_id: "",
      kb_ids: kb_ids.value,
    };

    console.log('发送数据:', askData);

    let response = await fetch('http://127.0.0.1/v1/conversation/ask', {
      method: 'POST',
      headers: headers.value,
      body: JSON.stringify(askData),
      signal: controller.value.signal
    });

    // 如果返回401错误，重新登录并重试
    if (response.status === 401) {
      console.log('Token过期，重新登录...');
      await login(); // 重新获取token
      
      // 使用新的token重试请求
      response = await fetch('http://127.0.0.1/v1/conversation/ask', {
        method: 'POST',
        headers: headers.value,
        body: JSON.stringify(askData),
        signal: controller.value.signal
      });
    }

    if (!response.ok) {
      console.error('ask 请求失败，状态码:', response.status);
      const errorText = await response.text();
      console.error('ask 响应内容:', errorText);
      throw new Error('请求失败');
    }

    // 处理流式响应
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let answerContent = "";
    let isThinking = false; // 添加思考状态标记
    let references = []; // 存储引用数据
    let buffer = ""; // 添加缓冲区来处理不完整的数据
    let hasReceivedValidData = false; // 标记是否收到有效数据

    console.log('开始接收流式响应...');

    let done = false;
    while (!done) {
      const { value, done: readerDone } = await reader.read();
      done = readerDone;
      
      if (done) {
        console.log('流式响应结束');
        break;
      }
      
      // 解码响应数据并添加到缓冲区
      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;
      console.log('收到原始数据块:', chunk);
      
      // 处理缓冲区中的完整行
      const lines = buffer.split('\n');
      // 保留最后一个可能不完整的行
      buffer = lines.pop() || '';
      
      for (const line of lines) {
        if (line.startsWith('data:')) {
          const dataStr = line.substring(5).trim();
          if (dataStr === '[DONE]' || dataStr === '') continue;
          
          try {
            const data = JSON.parse(dataStr);
            console.log('解析后的数据:', data);
            
            // 检查是否有错误
            if (data.code && data.code !== 0) {
              console.error('流式响应中的错误:', data);
              throw new Error(data.message || '请求失败');
            }
            
            if (data.data && data.data.answer) {
              const currentAnswerChunk = data.data.answer;

              isThinking = true;
              if (currentAnswerChunk.includes('</think>')) {
                isThinking = false;
              }

              answerContent = currentAnswerChunk;

              // 根据思考状态设置不同的样式
              if (isThinking) {
                mainAnswer.value = `<div class="think-block">${answerContent}`;
              } else {
                mainAnswer.value = answerContent;
              }

              console.log('收到最新回答:', answerContent);
              hasReceivedValidData = true;
              isLoading.value = false;
              hasResults.value = true;
            }

            if (data.data && data.data.reference) {
              const currentReferenceChunk = data.data.reference;

              // 处理引用数据
              if (currentReferenceChunk.chunks && Array.isArray(currentReferenceChunk.chunks)) {
                const newReferences = currentReferenceChunk.chunks.map(chunk => ({
                  content: chunk.content || '',
                  document_id: chunk.document_id || null,
                  document_name: chunk.document_name || '未知文档'
                }));
                
                // 累积引用数据，而不是覆盖
                references = [...references, ...newReferences];
                
                // 更新引用数据
                referencePopup.value.references = references;
                console.log('累积更新引用数据，当前总数:', references.length);
                console.log('最新引用数据:', newReferences);
              }

              // 处理文件引用
              if (currentReferenceChunk.files && Array.isArray(currentReferenceChunk.files)) {
                const newFiles = currentReferenceChunk.files.map(file => ({
                  content: file.content || '',
                  document_id: file.document_id || null,
                  document_name: file.document_name || '未知文档'
                }));
                referencePopup.value.files = [...referencePopup.value.files, ...newFiles];
                console.log('累积更新文件引用，当前总数:', referencePopup.value.files.length);
                console.log('最新文件引用:', newFiles);
              }

              console.log('参考文献：', currentReferenceChunk);
              console.log('当前引用弹出框状态:', referencePopup.value);
            }
          } catch (e) {
            console.error('JSON解析失败:', e);
            console.error('原始数据:', dataStr);
            console.error('当前缓冲区:', buffer);
            
            // 如果解析失败且包含错误信息，抛出错误
            if (dataStr.includes('"code":401') || dataStr.includes('Unauthorized')) {
              throw new Error('认证失败，请重新登录');
            } else if (dataStr.includes('"code":500') || dataStr.includes('Internal Server Error')) {
              throw new Error('服务器内部错误');
            } else if (dataStr.includes('"code":404') || dataStr.includes('Not Found')) {
              throw new Error('请求的资源不存在');
            }
            // 继续处理，不中断流程
          }
        }
      }
    }

    // 处理缓冲区中剩余的数据
    if (buffer.trim()) {
      console.log('处理剩余缓冲区数据:', buffer);
      const lines = buffer.split('\n');
      for (const line of lines) {
        if (line.startsWith('data:')) {
          const dataStr = line.substring(5).trim();
          if (dataStr === '[DONE]' || dataStr === '') continue;
          
          try {
            const data = JSON.parse(dataStr);
            console.log('解析剩余数据:', data);
            
            // 检查剩余数据中是否有错误
            if (data.code && data.code !== 0) {
              console.error('剩余数据中的错误:', data);
              throw new Error(data.message || '请求失败');
            }
            // 处理剩余数据...
          } catch (e) {
            console.error('解析剩余数据失败:', e);
            
            // 如果解析失败且包含错误信息，抛出错误
            if (dataStr.includes('"code":401') || dataStr.includes('Unauthorized')) {
              throw new Error('认证失败，请重新登录');
            } else if (dataStr.includes('"code":500') || dataStr.includes('Internal Server Error')) {
              throw new Error('服务器内部错误');
            } else if (dataStr.includes('"code":404') || dataStr.includes('Not Found')) {
              throw new Error('请求的资源不存在');
            }
          }
        }
      }
    }

    console.log('流式响应处理完成');
    
    // 如果没有收到任何有效数据，显示错误
    if (!hasReceivedValidData) {
      console.log('未收到有效数据，显示错误');
      hasError.value = true;
      errorMessage.value = '未收到有效响应，请重试';
      isLoading.value = false;
      mainAnswer.value = '';
      hasResults.value = false;
      return;
    }

  } catch (error) {
    // 修复后代码
    const isAbortError = error.name === 'AbortError';
    if (!isAbortError) {
      console.error('发送消息失败:', error);
      
      // 根据错误类型提供更详细的错误信息
      let detailedErrorMessage = '抱歉，发生了错误，请稍后重试。';
      
      if (error.message) {
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
          detailedErrorMessage = '网络连接失败，请检查网络连接后重试。';
        } else if (error.message.includes('timeout') || error.message.includes('Timeout')) {
          detailedErrorMessage = '请求超时，请稍后重试。';
        } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
          detailedErrorMessage = '认证失败，正在重新登录...';
        } else if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
          detailedErrorMessage = '服务器内部错误，请稍后重试。';
        } else if (error.message.includes('404') || error.message.includes('Not Found')) {
          detailedErrorMessage = '请求的资源不存在，请检查问题内容。';
        } else {
          detailedErrorMessage = `生成失败：${error.message}`;
        }
      }
      
      // 更新错误状态
      hasError.value = true;
      errorMessage.value = detailedErrorMessage;
      isLoading.value = false;
      
      // 清空"正在生成中"的内容
      mainAnswer.value = '';
      hasResults.value = false;
    } else {
      console.log('请求被取消');
      // 如果是取消请求，重置状态
      isLoading.value = false;
      mainAnswer.value = '';
      hasResults.value = false;
    }
  } finally {
    isLoading.value = false;
  }
};

// 获取检索测试结果
const getRetrievalTest = async () => {
  try {
    const payload = {
      kb_id: kb_ids.value,
      highlight: true,
      question: question.value,
      page: 1,
      size: 10,
    };

    console.log('发送检索测试请求的payload:', payload);

    let response = await fetch('http://127.0.0.1/v1/chunk/retrieval_test', {
      method: 'POST',
      headers: headers.value,
      body: JSON.stringify(payload)
    });

    // 如果返回401错误，重新登录并重试
    if (response.status === 401) {
      console.log('Token过期，重新登录...');
      await login(); // 重新获取token
      
      // 使用新的token重试请求
      response = await fetch('http://127.0.0.1/v1/chunk/retrieval_test', {
        method: 'POST',
        headers: headers.value,
        body: JSON.stringify(payload)
      });
    }

    console.log('检索测试响应状态码:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('检索测试失败，响应内容:', errorText);
      
      let errorMessage = '检索测试请求失败';
      if (response.status === 401) {
        errorMessage = '认证失败，请重新登录';
      } else if (response.status === 500) {
        errorMessage = '服务器内部错误';
      } else if (response.status === 404) {
        errorMessage = '知识库不存在或已被删除';
      } else if (response.status === 400) {
        errorMessage = '请求参数错误';
      }
      
      throw new Error(`${errorMessage} (状态码: ${response.status})`);
    }

    const result = await response.json();
    console.log('检索测试返回的完整结果:', result);
    
    if (result.data && result.data.chunks && result.data.doc_aggs) {
      // 创建文档ID到文档名称的映射
      const docNameMap = {};
      if (result.data.doc_aggs) {
        result.data.doc_aggs.forEach(doc => {
          if (doc.doc_id && doc.doc_name) {
            docNameMap[doc.doc_id] = doc.doc_name;
          }
        });
      }
      
      console.log('文档名称映射:', docNameMap);
      
      // 处理chunks数组，使用highlight作为内容，doc_id查找对应的doc_name
      relatedDocs.value = result.data.chunks.map((chunk, index) => {
        const docName = docNameMap[chunk.doc_id] || '未知文档';
        
        // 优先使用highlight字段，如果没有则使用content字段
        let contentToProcess = chunk.highlight || chunk.content || '';
        
        // 处理em标签，转换为高亮样式
        let processedContent = '';
        if (contentToProcess) {
          // 将 <em> 标签替换为 highlight-text 样式
          processedContent = contentToProcess.replace(/<em>(.*?)<\/em>/g, '<span class="highlight-text">$1</span>');
          console.log(`文档 ${index} 高亮处理:`, {
            original: contentToProcess,
            processed: processedContent
          });
        }
        
        return {
          content: processedContent,
          content_with_weight: chunk.content_with_weight || chunk.content || '',
          document_id: chunk.doc_id || null,
          doc_name: docName,
          index: index, // 添加索引用于引用
          isHovered: false
        };
      });
      
      console.log('处理后的相关文档:', relatedDocs.value);
    }
  } catch (error) {
    console.error('检索测试失败:', error);
    // 不抛出错误，让流程继续
  }
};

// 获取相关问题
const getRelatedQuestions = async () => {
  try {
    const payload = {
      question: question.value
    };

    console.log('发送相关问题请求的payload:', payload);

    let response = await fetch('http://127.0.0.1/v1/conversation/related_questions', {
      method: 'POST',
      headers: headers.value,
      body: JSON.stringify(payload)
    });

    // 如果返回401错误，重新登录并重试
    if (response.status === 401) {
      console.log('Token过期，重新登录...');
      await login(); // 重新获取token
      
      // 使用新的token重试请求
      response = await fetch('http://127.0.0.1/v1/conversation/related_questions', {
        method: 'POST',
        headers: headers.value,
        body: JSON.stringify(payload)
      });
    }

    console.log('相关问题响应状态码:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('相关问题请求失败，响应内容:', errorText);
      
      let errorMessage = '相关问题请求失败';
      if (response.status === 401) {
        errorMessage = '认证失败，请重新登录';
      } else if (response.status === 500) {
        errorMessage = '服务器内部错误';
      } else if (response.status === 404) {
        errorMessage = '服务不可用';
      } else if (response.status === 400) {
        errorMessage = '问题格式错误';
      }
      
      throw new Error(`${errorMessage} (状态码: ${response.status})`);
    }

    const result = await response.json();
    console.log('相关问题返回的完整结果:', result);
    
    if (result.data && Array.isArray(result.data)) {
      relatedQuestions.value = result.data;
      console.log('相关问题列表:', relatedQuestions.value);
    }
  } catch (error) {
    console.error('相关问题获取失败:', error);
    // 不抛出错误，让流程继续
  }
};

// 选择相关问题
const selectQuestion = async (newQuestion) => {
  console.log('选择相关问题:', newQuestion);
  
  // 更新当前问题
  question.value = newQuestion;
  
  // 重置状态
  isLoading.value = true;
  hasResults.value = false;
  hasError.value = false;
  errorMessage.value = '';
  mainAnswer.value = '';
  relatedDocs.value = [];
  relatedQuestions.value = [];
  
  // 清空引用弹出框数据
  referencePopup.value = {
    visible: false,
    references: [],
    displayReferences: [],
    position: { x: 0, y: 0 },
    files: []
  };
  
  // 更新路由（可选，用于浏览器历史记录）
  router.push({
    path: '/knowledge-qa-result',
    query: { question: newQuestion }
  });
  
  // 直接执行搜索
  try {
    await performSearch();
  } catch (error) {
    console.error('相关问题搜索失败:', error);
    hasError.value = true;
    errorMessage.value = '搜索失败，请重试';
  } finally {
    isLoading.value = false;
  }
};

// Markdown渲染
const renderMarkdown = (content) => {
  if (!content) return '';
  let processedContent = marked(content);
  processedContent = processedContent.replace(
    /<think>([\s\S]*?)<\/think>/g,
    '<div class="think-block">$1</div>'
  );
  processedContent = processedContent.replace(
    /##(\d+)\$\$/g,
    (match, number) => {
      const referenceIndex = parseInt(number);
      return `<span class="reference-icon-wrapper" data-reference-number="${referenceIndex}">
        <el-icon class="number-icon"><InfoFilled /></el-icon>
        <span class="number-badge">${number}</span>
      </span>`;
    }
  );
  return DOMPurify.sanitize(processedContent);
};

// 监听路由变化
watch(() => route.query.question, (newQuestion) => {
  // 只在组件初始化时或者手动输入URL时触发
  // 避免与selectQuestion的直接搜索冲突
  if (newQuestion && newQuestion !== question.value && !isLoading.value) {
    console.log('路由变化触发搜索:', newQuestion);
    question.value = newQuestion;
    performSearch();
  }
}, { immediate: false });

// 组件挂载时初始化
onMounted(async () => {
  if (!question.value) {
    hasError.value = true;
    errorMessage.value = '未找到搜索问题';
    isLoading.value = false;
    return;
  }

  try {
    await login();
    
    // 从路由参数获取选中的知识库ID
    const selectedKbIdFromRoute = route.query.selectedKbId;
    if (selectedKbIdFromRoute) {
      kb_ids.value = [selectedKbIdFromRoute];
      console.log('使用从主页面传递的知识库:', selectedKbIdFromRoute);
    } else {
      // 如果没有传递知识库ID，显示错误
      hasError.value = true;
      errorMessage.value = '未找到知识库信息';
      isLoading.value = false;
      return;
    }
    
    // 如果已经有知识库ID，直接开始搜索
    if (kb_ids.value.length > 0) {
      await performSearch();
    }
    
    // 添加点击页面其他地方关闭弹出框的事件监听
    document.addEventListener('click', handleDocumentClick);
  } catch (error) {
    hasError.value = true;
    errorMessage.value = error.message || '初始化失败';
    isLoading.value = false;
  }
});

// 组件卸载时移除事件监听
onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick);
});

// 关闭引用弹出组件
const closeReferencePopup = () => {
  referencePopup.value.visible = false;
  // 不清空 displayReferences，保持数据完整性
};

// 处理文档点击事件，关闭引用弹出框
const handleDocumentClick = (event) => {
  // 检查是否点击了引用图标
  const referenceIcon = event.target.closest('.reference-icon-wrapper');
  if (referenceIcon) {
    const referenceNumber = referenceIcon.getAttribute('data-reference-number');
    
    // 获取点击位置
    const rect = referenceIcon.getBoundingClientRect();
    
    console.log('点击的引用编号:', referenceNumber);
    console.log('当前引用弹出框状态:', referencePopup.value);
    console.log('引用数据数组长度:', referencePopup.value.references ? referencePopup.value.references.length : 0);
    console.log('引用数据数组:', referencePopup.value.references);
    
    // 根据引用编号查找对应的引用内容，编号从0开始
    const referenceIndex = parseInt(referenceNumber);
    const reference = referencePopup.value.references[referenceIndex];
    
    console.log('查找的索引:', referenceIndex);
    console.log('找到的引用:', reference);
    
    if (reference) {
      console.log('显示引用弹出框，引用数据:', reference);
      
      // 只更新需要的属性，不覆盖整个对象
      referencePopup.value.visible = true;
      referencePopup.value.displayReferences = [reference]; // 只显示当前引用的内容
      referencePopup.value.position = {
        x: rect.left + rect.width / 2,
        y: rect.top - 10 // 向上偏移10px
      };
      
      console.log('引用弹出框数据:', referencePopup.value);
    } else {
      console.log('未找到对应的引用数据，索引:', referenceIndex);
      console.log('当前引用数据:', referencePopup.value.references);
      console.log('引用数据数组长度:', referencePopup.value.references ? referencePopup.value.references.length : 0);
      
      // 如果找不到引用，尝试显示所有引用数据用于调试
      if (referencePopup.value.references && referencePopup.value.references.length > 0) {
        console.log('所有引用数据:');
        referencePopup.value.references.forEach((ref, idx) => {
          console.log(`索引 ${idx}:`, ref);
        });
      }
    }
    return;
  }
  
  // 检查是否点击了相关文档
  const docItem = event.target.closest('.doc-item');
  if (docItem) {
    // 相关文档的点击事件已经在模板中处理，这里不需要额外处理
    return;
  }
  
  // 如果点击的不是引用图标、相关文档或弹出框，则关闭弹出框
  if (!event.target.closest('.reference-popup')) {
    closeReferencePopup();
  }
};

// 显示文档参考
const showDocReference = (doc, event) => {
  // 获取点击位置
  const rect = event.currentTarget.getBoundingClientRect();
  
  // 将文档数据转换为引用格式，确保包含高亮
  const reference = {
    content: doc.content || '', // doc.content 已经包含高亮处理
    document_id: doc.document_id || null,
    document_name: doc.doc_name || '未知文档'
  };
  
  // 创建文件数据
  const files = [{
    doc_id: doc.document_id,
    doc_name: doc.doc_name || '未知文档'
  }];
  
  console.log('显示文档参考:', reference);
  console.log('文件数据:', files);
  
  // 显示引用弹出框
  referencePopup.value.visible = true;
  referencePopup.value.displayReferences = [reference];
  referencePopup.value.files = files;
  referencePopup.value.position = {
    x: rect.left + rect.width / 2,
    y: rect.top - 10
  };
  
  console.log('文档参考弹出框数据:', referencePopup.value);
};

// 处理文件点击事件
const handleFileClick = (file) => {
  selectedFile.value = file;
  filePreviewVisible.value = true;
  console.log('文件预览弹出，文件:', file);
};

// 关闭文件预览
const closeFilePreview = () => {
  filePreviewVisible.value = false;
  selectedFile.value = null;
  console.log('文件预览关闭');
};

// 获取文件类型
const getFileType = (fileName) => {
  if (!fileName) return '';
  const lowerCaseFileName = fileName.toLowerCase();
  if (lowerCaseFileName.endsWith('.pdf')) return 'pdf';
  if (lowerCaseFileName.endsWith('.docx')) return 'docx';
  if (lowerCaseFileName.endsWith('.doc')) return 'doc';
  if (lowerCaseFileName.endsWith('.xls') || lowerCaseFileName.endsWith('.xlsx')) return 'excel';
  if (lowerCaseFileName.endsWith('.ppt') || lowerCaseFileName.endsWith('.pptx')) return 'ppt';
  if (lowerCaseFileName.endsWith('.txt')) return 'txt';
  if (lowerCaseFileName.endsWith('.md')) return 'markdown';
  return '';
};
</script>

<style scoped>
.knowledge-qa-result-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  position: relative;
  overflow-x: hidden;
}

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
  overflow: hidden;
  max-width: 100vw;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(13, 110, 253, 0.05);
  backdrop-filter: blur(10px);
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: -100px;
  right: -100px;
  animation: float 6s ease-in-out infinite;
}

.circle-2 {
  width: 150px;
  height: 150px;
  bottom: -75px;
  left: -75px;
  animation: float 8s ease-in-out infinite reverse;
}

.circle-3 {
  width: 100px;
  height: 100px;
  top: 50%;
  right: 10%;
  animation: float 10s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

.content-container {
  position: relative;
  z-index: 2;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(13, 110, 253, 0.1);
}

.title-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 12px;
}

.icon-wrapper {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(13, 110, 253, 0.2);
}

.title-icon {
  font-size: 28px;
  color: white;
}

.main-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  color: #212529;
}

.header-subtitle {
  font-size: 1.1rem;
  color: #6c757d;
  font-weight: 500;
}

.question-section {
  margin-bottom: 40px;
}

.question-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(13, 110, 253, 0.1);
  transition: all 0.3s ease;
}

.question-container:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.question-icon {
  font-size: 24px;
  color: #0d6efd;
}

.question-container h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
  color: #212529;
}

.question-text {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #212529;
  padding: 24px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  border: 1px solid rgba(13, 110, 253, 0.1);
  font-weight: 500;
}

.loading-section,
.error-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 500px;
}

.loading-card,
.error-card {
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

.loading-content h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #212529;
  margin: 0 0 12px 0;
}

.loading-content p {
  color: #6c757d;
  font-size: 1rem;
  margin: 0 0 24px 0;
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

.results-section {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.main-answer,
.related-docs,
.related-questions {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(13, 110, 253, 0.1);
  transition: all 0.3s ease;
}

.main-answer:hover,
.related-docs:hover,
.related-questions:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.answer-header,
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(13, 110, 253, 0.1);
}

.answer-icon-wrapper,
.section-icon-wrapper {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(13, 110, 253, 0.2);
}

.answer-icon,
.section-icon {
  font-size: 20px;
  color: white;
}

.answer-header h3,
.section-header h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
  color: #212529;
  flex: 1;
}

.doc-count,
.question-count {
  background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 600;
}

.answer-content {
  line-height: 1.8;
  color: #212529;
  font-size: 1.05rem;
}

.docs-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.doc-item {
  background: rgba(248, 249, 250, 0.8);
  border: 2px solid rgba(13, 110, 253, 0.1);
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.doc-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.doc-item:hover::before {
  transform: scaleX(1);
}

.doc-item:hover {
  border-color: rgba(13, 110, 253, 0.3);
  background: rgba(248, 249, 250, 1);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(13, 110, 253, 0.15);
}

.doc-item-hover {
  border-color: rgba(13, 110, 253, 0.3) !important;
  background: rgba(248, 249, 250, 1) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 24px rgba(13, 110, 253, 0.15) !important;
}

.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.doc-title {
  font-weight: 600;
  color: #212529;
  font-size: 1.1rem;
}

.doc-index {
  background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
  color: white;
  padding: 4px 8px;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 600;
}

.doc-content {
  color: #6c757d;
  font-size: 0.95rem;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 16px;
}

.doc-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #0d6efd;
  font-size: 0.9rem;
  font-weight: 500;
}

.doc-footer-icon {
  font-size: 16px;
}

/* 相关文档内容中的高亮文本样式 */
.doc-content :deep(.highlight-text) {
  color: #dc3545;
  font-weight: bold;
  background: rgba(220, 53, 69, 0.1);
  padding: 2px 4px;
  border-radius: 4px;
}

.questions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.question-item {
  border-radius: 20px;
  padding: 12px 20px;
  font-size: 0.95rem;
  background: rgba(248, 249, 250, 0.8);
  border: 2px solid rgba(13, 110, 253, 0.1);
  color: #212529;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.question-item:hover {
  background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
  border-color: transparent;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(13, 110, 253, 0.3);
}

.question-item-icon {
  font-size: 14px;
  transition: transform 0.3s ease;
}

.question-item:hover .question-item-icon {
  transform: translateX(4px);
}

.error-content {
  text-align: center;
}

.error-icon-wrapper {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  box-shadow: 0 4px 16px rgba(220, 53, 69, 0.2);
}

.error-icon {
  font-size: 32px;
  color: white;
}

.error-content h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #212529;
  margin: 0 0 12px 0;
}

.error-content p {
  color: #6c757d;
  font-size: 1rem;
  margin: 0 0 24px 0;
  line-height: 1.6;
}

.retry-button {
  background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
  border: none;
  border-radius: 20px;
  padding: 12px 24px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.retry-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(13, 110, 253, 0.3);
}

.retry-icon {
  font-size: 16px;
}

/* Markdown样式 */
.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  line-height: 1.8;
  word-wrap: break-word;
}

.markdown-body :deep(p) {
  margin: 0 0 1.2em;
}

.markdown-body :deep(pre) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  padding: 20px;
  overflow: auto;
  border: 1px solid rgba(13, 110, 253, 0.1);
  margin: 1.2em 0;
}

.markdown-body :deep(code) {
  background: rgba(13, 110, 253, 0.1);
  border-radius: 6px;
  padding: 0.3em 0.6em;
  font-family: 'Fira Code', monospace;
  font-size: 0.9em;
  color: #0d6efd;
}

.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
  color: #212529;
}

.markdown-body :deep(ul), .markdown-body :deep(ol) {
  padding-left: 2em;
  margin: 1.2em 0;
}

.markdown-body :deep(blockquote) {
  border-left: 4px solid #0d6efd;
  margin: 1.2em 0;
  padding: 16px 20px;
  background: rgba(13, 110, 253, 0.05);
  border-radius: 0 8px 8px 0;
  color: #495057;
  font-style: italic;
}

.markdown-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1.2em 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.markdown-body :deep(th), .markdown-body :deep(td) {
  border: 1px solid rgba(13, 110, 253, 0.1);
  padding: 12px 16px;
}

.markdown-body :deep(th) {
  background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
  color: white;
  font-weight: 600;
}

.markdown-body :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin-top: 1.5em;
  margin-bottom: 1em;
  font-weight: 700;
  line-height: 1.3;
  color: #212529;
}

.markdown-body :deep(h1) { font-size: 2.2em; }
.markdown-body :deep(h2) { font-size: 1.8em; }
.markdown-body :deep(h3) { font-size: 1.5em; }
.markdown-body :deep(h4) { font-size: 1.3em; }
.markdown-body :deep(h5) { font-size: 1.1em; }
.markdown-body :deep(h6) { font-size: 1em; }

/* 思考过程的样式 */
.markdown-body :deep(.think-block) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-left: 4px solid #0d6efd;
  padding: 20px 24px 20px 48px;
  margin: 1.2em 0;
  font-style: italic;
  color: #495057;
  border-radius: 0 12px 12px 0;
  font-size: 0.95em;
  line-height: 1.7;
  position: relative;
  min-height: 40px;
  overflow: visible;
}

.markdown-body :deep(.think-block)::before {
  content: '💭';
  position: absolute;
  top: 20px;
  left: 20px;
  font-size: 1.2em;
  opacity: 0.7;
  pointer-events: none;
  transform: none;
}

.markdown-body :deep(.think-block p) {
  margin: 0;
}

.markdown-body :deep(.think-block p + p) {
  margin-top: 12px;
}

/* 数字图标和徽章样式 */
.markdown-body :deep(.number-icon) {
  color: #0d6efd;
  font-size: 16px;
  vertical-align: middle;
  margin-right: 4px;
}

.markdown-body :deep(.number-badge) {
  background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  vertical-align: middle;
  margin-left: 4px;
  line-height: 1;
  padding: 0;
  min-width: 18px;
  min-height: 18px;
  box-shadow: 0 2px 6px rgba(13, 110, 253, 0.3);
}

/* 引用图标包装器样式 */
.markdown-body :deep(.reference-icon-wrapper) {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
  transition: all 0.3s ease;
  margin: 0 4px;
  background: rgba(13, 110, 253, 0.1);
}

.markdown-body :deep(.reference-icon-wrapper:hover) {
  background: rgba(13, 110, 253, 0.2);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
}

.markdown-body :deep(.reference-icon-wrapper:active) {
  transform: scale(0.95);
}

.highlight-text {
  color: #e74c3c;
  font-weight: bold;
  background: rgba(231, 76, 60, 0.1);
  padding: 2px 4px;
  border-radius: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .knowledge-qa-result-view {
    padding: 16px;
  }
  
  .content-container {
    padding: 16px;
  }
  
  .main-title {
    font-size: 1.8rem;
  }
  
  .question-text {
    font-size: 1rem;
  }
  
  .answer-card {
    padding: 20px;
  }
  
  .related-questions {
    grid-template-columns: 1fr;
  }
  
  .reference-popup {
    width: 95%;
    max-width: none;
  }
}

.reference-content {
  max-height: 400px;
  overflow-y: auto;
}

.reference-text {
  color: #333;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

/* 引用弹窗中的高亮文本样式 */
.reference-text :deep(.highlight-text) {
  color: #e74c3c;
  font-weight: bold;
  background: rgba(231, 76, 60, 0.1);
  padding: 2px 4px;
  border-radius: 4px;
}

.reference-files {
  border-top: 1px solid #e4e7ed;
  padding-top: 16px;
}

.reference-files h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  transition: all 0.2s ease;
}

.file-item:hover {
  border-color: #409EFF;
  background-color: #f0f7ff;
}

.file-item .el-icon {
  color: #409EFF;
  font-size: 16px;
}

.file-item span {
  font-size: 14px;
  color: #606266;
}

/* 去除主内容区的多余滚动条和高度限制，只保留弹窗等需要滚动的地方 */
.knowledge-qa-result-view,
.content-container,
.results-section,
.main-answer,
.related-docs,
.related-questions {
  max-height: none !important;
  overflow: visible !important;
}

/* 错误显示样式 */
.error-section {
  margin-top: 40px;
}

.error-card {
  background: linear-gradient(135deg, #fff5f5 0%, #fef2f2 100%);
  border: 1px solid #fecaca;
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.1);
}

.error-content {
  max-width: 500px;
  margin: 0 auto;
}

.error-icon-wrapper {
  margin-bottom: 20px;
}

.error-icon {
  font-size: 48px;
  color: #ef4444;
}

.error-card h3 {
  font-size: 24px;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 16px;
}

.error-message {
  font-size: 16px;
  color: #7f1d1d;
  margin-bottom: 24px;
  line-height: 1.6;
  background: rgba(239, 68, 68, 0.05);
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #ef4444;
}

.error-suggestions {
  text-align: left;
  margin-bottom: 24px;
  background: rgba(255, 255, 255, 0.8);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #fecaca;
}

.error-suggestions h4 {
  font-size: 16px;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 12px;
}

.error-suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.error-suggestions li {
  font-size: 14px;
  color: #7f1d1d;
  margin-bottom: 8px;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.retry-button {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border: none;
  padding: 12px 24px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.retry-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.back-button {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #64748b;
  padding: 12px 24px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #475569;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .error-card {
    padding: 24px 16px;
  }
  
  .error-actions {
    flex-direction: column;
  }
  
  .error-suggestions {
    padding: 16px;
  }
}
</style>
