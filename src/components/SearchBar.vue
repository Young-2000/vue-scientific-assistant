<template>
  <div class="search-bar">
    <el-input
      v-model="query"
      placeholder="搜索、提示或发消息"
      size="large"
      style="width: 100%; max-width: 600px;"
    >
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
    </el-input>
    <div style="margin-top: 10px;">
      <el-button type="primary" @click="onSearch">深度思考</el-button>
      <el-button>公开库</el-button>
      <el-button>私有库</el-button>
      <el-button>团队库</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Search } from '@element-plus/icons-vue';

const query = ref('');

const onSearch = () => {
  // 搜索按钮逻辑（调用 API 或处理查询）
  console.log('搜索内容：', query.value);
};
</script>

<style scoped>
.search-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.search-bar .el-button + .el-button {
  margin-left: 10px;
}
</style>
