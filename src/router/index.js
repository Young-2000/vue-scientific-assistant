import { createRouter, createWebHistory } from 'vue-router'
import IntelligentSearch from '@/views/IntelligentSearch.vue'
import AIWriting from '@/views/AIWriting.vue'
import ReportGeneration from '@/views/ReportGeneration.vue'
import PolicyQA from '@/views/PolicyQA.vue'
import LiteratureReview from '@/views/LiteratureReview.vue'
import Dubbing from '@/views/Dubbing.vue'
import PPTGeneration from '@/views/PPTGeneration.vue'
import TranslationComparison from '@/views/TranslationComparison.vue'
import SummaryReport from '@/views/SummaryReport.vue'

const routes = [
  { path: '/', redirect: '/search' },
  { path: '/search', name: '智能搜索', component: IntelligentSearch },
  { path: '/writing', name: 'AI写作', component: AIWriting },
  { path: '/report', name: '报告生成', component: ReportGeneration },
  { path: '/policy', name: '政策问答', component: PolicyQA },
  { path: '/literature', name: '文献研读', component: LiteratureReview },
  { path: '/dubbing', name: '智能配音', component: Dubbing },
  { path: '/ppt', name: 'PPT生成', component: PPTGeneration },
  { path: '/translation', name: '翻译对比', component: TranslationComparison },
  { path: '/summary', name: '总结汇报', component: SummaryReport },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
