<template>
  <el-card class="module-card" shadow="hover">
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

// eslint-disable-next-line no-undef
defineProps({
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
  }
});
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
