<template>
  <el-card class="module-card" shadow="hover" @click="handleCardClick">
    <div class="card-content">
      <div class="icon-container">
        <el-icon :size="18">
          <component :is="icon || Menu" />
        </el-icon>
      </div>
      <div class="text-container">
        <h3>{{ title }}</h3>
        <p>{{ description }}</p>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { Menu } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// eslint-disable-next-line no-undef
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  icon: {
    type: Object,
    default: null
  },
  route: {
    type: String,
    default: ''
  }
});

// 处理卡片点击事件
const handleCardClick = () => {
  // 如果有指定的路由，直接跳转到对应页面
  if (props.route) {
    router.push(props.route);
    return;
  }
  
  // 如果没有指定路由，使用原来的聊天界面逻辑（作为备用）
  let initialMessage = '';
  
  switch (props.title) {
    case 'AI写作':
      initialMessage = '请帮我进行AI写作，我需要分步骤生成文纲和文稿。';
      break;
    case '报告生成':
      initialMessage = '请帮我生成一份深度研究报告，需要精准分析。';
      break;
    case 'OCR识别':
      initialMessage = '请帮我进行OCR文字识别。';
      break;
    default:
      initialMessage = `请帮我使用${props.title}功能：${props.description}`;
  }
  
  // 跳转到聊天界面，传递初始消息
  router.push({
    path: '/chat',
    query: { initialMessage: initialMessage }
  });
};
</script>

<style scoped>
.module-card {
  width: 260px;
  height: 90px;
  margin: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #ebeef5;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.module-card:hover {
  transform: scale(1.02);
}

.card-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.icon-container {
  margin-right: 16px;
  color: #409EFF;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f7ff;
}

.text-container h3 {
  margin: 0 0 6px 0;
  font-size: 15px;
  font-weight: 500;
}

.text-container p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}
</style>
