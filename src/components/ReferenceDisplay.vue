<template>
  <div 
    v-if="visible" 
    class="reference-popup"
    :style="popupStyle"
    @click.stop
  >
    <div class="popup-arrow"></div>
    <div class="popup-content">
      <div 
        v-for="(reference, index) in props.references" 
        :key="index" 
        class="reference-item"
      >
        <div class="reference-text" v-if="reference.content">
          {{ reference.content }}
        </div>
        
        <!-- 文件展示组件 -->
        <FileDisplay 
          v-if="reference.content && getFilesForReference(reference).length > 0"
          :files="getFilesForReference(reference)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import FileDisplay from './FileDisplay.vue';

// 定义组件属性
// eslint-disable-next-line no-undef
const props = defineProps({
  references: {
    type: Array,
    default: () => []
  },
  visible: {
    type: Boolean,
    default: false
  },
  position: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  },
  files: {
    type: Array,
    default: () => []
  }
});

// 响应式的位置状态
const currentPosition = ref({ x: 0, y: 0 });

// 监听位置变化
watch(() => props.position, (newPosition) => {
  currentPosition.value = { ...newPosition };
}, { immediate: true });

// 计算弹窗位置样式
const popupStyle = computed(() => {
  return {
    left: `${currentPosition.value.x}px`,
    top: `${currentPosition.value.y}px`
  };
});

// 滚动事件处理函数
const handleScroll = () => {
  // 当滚动时直接关闭弹窗，避免位置计算问题
  if (props.visible) {
    emit('close');
  }
};

// 定义emit
// eslint-disable-next-line no-undef
const emit = defineEmits(['close']);

// 组件挂载时添加滚动监听
onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true });
});

// 组件卸载时移除滚动监听
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});

// 根据引用内容匹配对应的文件
const getFilesForReference = (reference) => {
  console.log('getFilesForReference called with:', reference);
  console.log('Available files:', props.files);
  
  if (!reference.document_id || !props.files || props.files.length === 0) {
    console.log('No document_id or no files available');
    return [];
  }
  
  // 根据document_id匹配对应的文件
  const matchedFiles = props.files.filter(file => file.doc_id === reference.document_id);
  console.log('Matched files:', matchedFiles);
  
  return matchedFiles;
};
</script>

<style scoped>
.reference-popup {
  position: fixed;
  z-index: 9999;
  max-width: 600px;
  min-width: 400px;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translate(-50%, -100%);
  margin-top: -10px;
}

.popup-arrow {
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 8px solid #e9ecef;
}

.popup-arrow::after {
  content: '';
  position: absolute;
  bottom: 1px;
  left: -7px;
  width: 0;
  height: 0;
  border-left: 7px solid transparent;
  border-right: 7px solid transparent;
  border-top: 7px solid white;
}

.popup-content {
  padding: 16px;
}

.reference-item {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 12px;
}

.reference-item:last-child {
  margin-bottom: 0;
}

.reference-text {
  color: #333;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
  margin-bottom: 8px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

/* 文件展示组件在引用中的样式 */
.reference-item :deep(.file-display) {
  margin-top: 8px;
  padding: 8px;
  background-color: #f0f7ff;
  border-radius: 4px;
  border: 1px solid #d1e7ff;
}

.reference-item :deep(.file-list) {
  gap: 6px;
}

.reference-item :deep(.file-item) {
  padding: 4px 8px;
  font-size: 12px;
  max-width: 150px;
}
</style> 