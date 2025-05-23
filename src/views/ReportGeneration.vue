<template>
  <div>
    <h2>报告生成</h2>
    <p>深度研究，精准分析</p>
    <el-input
      v-model="reportQuery"
      placeholder="请输入研究主题或报告需求"
      style="width: 400px;"
    ></el-input>
    <el-button type="primary" @click="generateReport" style="margin-left: 10px;">
      生成报告
    </el-button>
    <div v-if="reportResult" style="margin-top: 20px;">
      <h3>报告结果：</h3>
      <el-card class="box-card">
        <pre>{{ reportResult }}</pre>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const reportQuery = ref('');
const reportResult = ref('');

const generateReport = () => {
  if (reportQuery.value.trim() === '') {
    alert('请输入研究主题');
    return;
  }
  // 这里可以调用API接口获取报告数据（示例留空）
  reportResult.value = '这是根据主题生成的报告内容（示例）。';
};
</script>

<style scoped>
h2 {
  margin-bottom: 0;
}
p {
  color: #606266;
  margin-top: 5px;
}
.box-card {
  white-space: pre-wrap;
}
</style> 