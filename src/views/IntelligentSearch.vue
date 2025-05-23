<template>
  <div>
    <h2>智能搜索</h2>
    <p>实时资讯，丰富信源，整合搜索</p>
    <!-- 搜索输入组件 -->
    <SearchBar />

    <!-- 功能模块入口卡片 -->
    <div class="module-cards" style="display: flex; flex-wrap: wrap; margin-top: 20px;">
      <el-card class="box-card" style="width: 300px; margin: 10px;">
        <h3>AI写作</h3>
        <p>分步骤生成文纲和文稿</p>
      </el-card>
      <el-card class="box-card" style="width: 300px; margin: 10px;">
        <h3>报告生成</h3>
        <p>深度研究，精准分析</p>
      </el-card>
      <el-card class="box-card" style="width: 300px; margin: 10px;">
        <h3>政策问答</h3>
        <p>理解政策，解读政策</p>
      </el-card>
      <el-card class="box-card" style="width: 300px; margin: 10px;">
        <h3>文献研读</h3>
        <p>提炼大纲，总结摘要</p>
      </el-card>
      <el-card class="box-card" style="width: 300px; margin: 10px;">
        <h3>智能配音</h3>
        <p>为你的文字赋予声音</p>
      </el-card>
      <el-card class="box-card" style="width: 300px; margin: 10px;">
        <h3>PPT生成</h3>
        <p>打造精彩的演讲内容</p>
      </el-card>
      <el-card class="box-card" style="width: 300px; margin: 10px;">
        <h3>翻译对比</h3>
        <p>双语阅读，对照理解</p>
      </el-card>
      <el-card class="box-card" style="width: 300px; margin: 10px;">
        <h3>总结汇报</h3>
        <p>凝练你的工作成效</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import SearchBar from '@/components/SearchBar.vue';
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
  cursor: pointer;
}
</style> 