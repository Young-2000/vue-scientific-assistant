import { createRouter, createWebHistory } from 'vue-router'
import IntelligentSearch from '@/views/IntelligentSearch.vue'
import ReportGeneration from '@/views/ReportGeneration.vue'
import ReportResult from '@/views/ReportResult.vue'
import KnowledgeQA from '@/views/KnowledgeQA.vue'
import KnowledgeQAResult from '@/views/KnowledgeQAResult.vue'
import OCRRecognition from '@/views/OCRRecognition.vue'
import ChatInterface from '../components/ChatInterface.vue'
import AIWriting from '@/views/AIWriting.vue'

const routes = [
  { path: '/', redirect: '/search' },
  { path: '/search', name: '智能搜索', component: IntelligentSearch },
  { path: '/report', name: '报告生成', component: ReportGeneration },
  { path: '/report-result', component: ReportResult },
  { path: '/knowledge-qa', name: '知识库问答', component: KnowledgeQA },
  { 
    path: '/knowledge-qa-result', 
    name: '知识库问答结果', 
    component: KnowledgeQAResult,
    props: (route) => ({ question: route.query.question })
  },
  { path: '/ocr', name: 'OCR识别', component: OCRRecognition },
  { path: '/ai-writing', name: 'AI写作', component: AIWriting },
  {
    path: '/chat',
    name: 'chat',
    component: ChatInterface,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes
})

export default router
