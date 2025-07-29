<template>
  <div class="kb-stats">
    <el-card class="stats-card" shadow="hover">
      <template #header>
        <div class="stats-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>知识库统计</span>
        </div>
      </template>
      
      <div class="stats-content">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalKbs }}</div>
            <div class="stat-label">知识库总数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalDocs }}</div>
            <div class="stat-label">文档总数</div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { DataAnalysis } from '@element-plus/icons-vue';

const props = defineProps({
  knowledgeBases: {
    type: Array,
    default: () => []
  }
});

const stats = ref({
  totalKbs: 0,
  totalDocs: 0
});

const calculateStats = () => {
  const kbs = Array.isArray(props.knowledgeBases) ? props.knowledgeBases : [];
  
  stats.value = {
    totalKbs: kbs.length,
    totalDocs: kbs.reduce((sum, kb) => sum + (kb.doc_num || 0), 0)
  };
};

onMounted(() => {
  calculateStats();
});

// 监听知识库数据变化
watch(() => props.knowledgeBases, () => {
  calculateStats();
}, { immediate: true });

// 暴露方法给父组件
defineExpose({
  refreshStats: calculateStats
});
</script>

<style scoped>
.kb-stats {
  margin-bottom: 20px;
}

.stats-card {
  border-radius: 12px;
}

.stats-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #333;
}

.stats-content {
  padding: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
  transition: transform 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
}
</style> 