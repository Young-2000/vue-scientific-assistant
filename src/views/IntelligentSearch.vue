<template>
  <div class="intelligent-search-view">
    <h2 class="main-title">智能搜索</h2>
    <p class="subtitle">实时资讯，丰富信源，整合搜索</p>
    
    <!-- 搜索输入组件（包含知识库选择） -->
    <SearchBar />
    
    <!-- 功能模块入口卡片 -->
    <div class="module-cards">
      <ModuleCard 
        v-for="module in modules" 
        :key="module.title"
        :title="module.title"
        :description="module.description"
        :icon="module.icon"
        :route="module.route"
      />
    </div>
  </div>
</template>

<script setup>
import SearchBar from '@/components/SearchBar.vue';
import ModuleCard from '@/components/ModuleCard.vue';
import { Edit, Document, PictureFilled, ChatLineRound } from '@element-plus/icons-vue';

const modules = [
  { title: 'AI写作', description: '分步骤生成文纲和文稿', icon: Edit, route: '/ai-writing' },
  { title: '报告生成', description: '深度研究，精准分析', icon: Document, route: '/report' },
  { title: '知识库问答', description: '基于知识库的智能问答', icon: ChatLineRound, route: '/knowledge-qa' },
  { title: 'OCR识别', description: '图片文字识别与提取', icon: PictureFilled, route: '/ocr' }
];
</script>

<style scoped>
.intelligent-search-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.main-title {
  font-size: 2.2rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 8px;
  color: #333;
}

.subtitle {
  font-size: 1rem;
  color: #999;
  text-align: center;
  margin-bottom: 40px;
}

.module-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 40px;
  width: 100%;
}

@media (max-width: 768px) {
  .intelligent-search-view {
    padding: 16px;
  }
  
  .main-title {
    font-size: 1.8rem;
  }
  
  .module-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
</style> 