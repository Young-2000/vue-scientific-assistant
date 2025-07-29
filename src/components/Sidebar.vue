<template>
  <div class="sidebar">
    <!-- Logo 区域 -->
    <div class="logo-area" style="display: flex; align-items: center; padding: 20px;">
      <img src="@/assets/logo.png" alt="Logo" style="width: 32px; margin-right: 10px;" />
      <h3 style="margin: 0; color: #409EFF;">科研助手</h3>
    </div>

    <!-- 功能模块导航 -->
    <el-menu
      class="el-menu-vertical-demo"
      :default-active="$route.path"
      :collapse="false"
      router
      background-color="#f5f7fa"
      text-color="#333"
      active-text-color="#409EFF"
    >
      <el-menu-item index="/search">智能搜索</el-menu-item>
      <el-menu-item index="/report">报告生成</el-menu-item>
      <el-menu-item index="/knowledge-qa">知识库问答</el-menu-item>
      <el-menu-item index="/knowledge-management">知识库管理</el-menu-item>
      <el-menu-item index="/ocr">OCR识别</el-menu-item>
      <el-menu-item index="/ai-writing">AI写作</el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
// 移除了 Plus 图标的导入，因为不再需要
</script>

<style scoped>
.sidebar {
  background-color: #f5f7fa;
  height: 100%;
}
</style>
