<template>
  <div class="kb-filter">
    <el-card class="filter-card" shadow="hover">
      <div class="filter-content">
        <!-- 搜索框 -->
        <div class="search-section">
          <el-input
            v-model="searchQuery"
            placeholder="搜索知识库名称..."
            clearable
            @input="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        
        <!-- 过滤选项 -->
        <div class="filter-section">
          
          <el-select
            v-model="sortBy"
            placeholder="排序方式"
            @change="handleSort"
            style="width: 140px;"
          >
            <el-option label="更新时间" value="update_time" />
            <el-option label="名称" value="name" />
            <el-option label="文档数量" value="doc_num" />
          </el-select>
          
          <el-radio-group v-model="sortOrder" @change="handleSort" size="small">
            <el-radio-button label="desc">降序</el-radio-button>
            <el-radio-button label="asc">升序</el-radio-button>
          </el-radio-group>
        </div>
        
        <!-- 快速操作 -->
        <div class="quick-actions">
          
          <el-button 
            type="primary" 
            link 
            @click="showOnlyEmpty"
            :class="{ active: showEmptyOnly }"
          >
            <el-icon><Folder /></el-icon>
            仅显示空知识库
          </el-button>
          
          <el-button 
            type="primary" 
            link 
            @click="resetFilters"
          >
            <el-icon><Refresh /></el-icon>
            重置筛选
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { Search, Folder, Refresh } from '@element-plus/icons-vue';

const props = defineProps({
  knowledgeBases: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['filtered']);

// 响应式数据
const searchQuery = ref('');
const sortBy = ref('update_time');
const sortOrder = ref('desc');
const showEmptyOnly = ref(false);

// 过滤和排序逻辑
const applyFilters = () => {
  // 确保 knowledgeBases 是数组
  const kbs = Array.isArray(props.knowledgeBases) ? props.knowledgeBases : [];
  let filtered = [...kbs];
  
  // 搜索过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(kb => 
      kb && kb.name && kb.name.toLowerCase().includes(query)
    );
  }
  

  
  // 仅显示空知识库
  if (showEmptyOnly.value) {
    filtered = filtered.filter(kb => kb && (kb.doc_num || 0) === 0);
  }
  
  // 排序
  filtered.sort((a, b) => {
    if (!a || !b) return 0;
    
    let aValue = a[sortBy.value];
    let bValue = b[sortBy.value];
    
    // 处理时间戳排序
    if (sortBy.value === 'update_time') {
      aValue = new Date(aValue || 0);
      bValue = new Date(bValue || 0);
    }
    
    // 处理字符串排序
    if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }
    
    // 处理数字排序
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      if (sortOrder.value === 'asc') {
        return aValue - bValue;
      } else {
        return bValue - aValue;
      }
    }
    
    // 处理字符串和日期排序
    if (sortOrder.value === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });
  
  emit('filtered', filtered);
};

// 事件处理
const handleSearch = () => {
  applyFilters();
};



const handleSort = () => {
  applyFilters();
};



const showOnlyEmpty = () => {
  showEmptyOnly.value = !showEmptyOnly.value;
  applyFilters();
};

const resetFilters = () => {
  searchQuery.value = '';
  sortBy.value = 'update_time';
  sortOrder.value = 'desc';
  showEmptyOnly.value = false;
  applyFilters();
};

// 监听知识库数据变化
watch(() => props.knowledgeBases, () => {
  applyFilters();
}, { immediate: true });

// 暴露方法给父组件
defineExpose({
  resetFilters,
  getFilters: () => ({
    searchQuery: searchQuery.value,
    sortBy: sortBy.value,
    sortOrder: sortOrder.value,
    showEmptyOnly: showEmptyOnly.value
  })
});
</script>

<style scoped>
.kb-filter {
  margin-bottom: 20px;
}

.filter-card {
  border-radius: 12px;
}

.filter-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-section {
  flex: 1;
}

.search-section :deep(.el-input__wrapper) {
  border-radius: 8px;
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-section :deep(.el-select .el-input__wrapper) {
  border-radius: 6px;
}

.quick-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.quick-actions .el-button {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.quick-actions .el-button:hover {
  transform: translateY(-1px);
}

.quick-actions .el-button.active {
  color: #409EFF;
  font-weight: 600;
}

.quick-actions .el-button.active::before {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #409EFF;
  border-radius: 1px;
}

@media (max-width: 768px) {
  .filter-content {
    gap: 12px;
  }
  
  .filter-section {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .filter-section .el-select {
    width: 100% !important;
  }
  
  .quick-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .quick-actions .el-button {
    justify-content: center;
  }
}
</style> 