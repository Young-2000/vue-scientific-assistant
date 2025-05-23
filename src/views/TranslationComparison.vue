<template>
  <div>
    <h2>翻译对比</h2>
    <p>双语阅读，对照理解</p>

    <!-- 原文输入 -->
    <el-input
      v-model="sourceText"
      type="textarea"
      :rows="6"
      placeholder="请输入需要翻译的文本..."
    ></el-input>

    <!-- 翻译选项 -->
    <div class="translation-options" style="margin-top: 20px;">
      <el-form :model="translationOptions" label-width="100px">
        <el-form-item label="目标语言">
          <el-select v-model="translationOptions.targetLang" placeholder="请选择目标语言">
            <el-option label="英语" value="en" />
            <el-option label="日语" value="ja" />
            <el-option label="韩语" value="ko" />
            <el-option label="法语" value="fr" />
            <el-option label="德语" value="de" />
          </el-select>
        </el-form-item>
        <el-form-item label="翻译风格">
          <el-select v-model="translationOptions.style" placeholder="请选择翻译风格">
            <el-option label="直译" value="literal" />
            <el-option label="意译" value="free" />
            <el-option label="学术" value="academic" />
            <el-option label="文学" value="literary" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <el-button type="primary" @click="translateText" style="margin-top: 20px;">
      开始翻译
    </el-button>

    <!-- 翻译结果 -->
    <div v-if="translationResult" style="margin-top: 20px;">
      <h3>翻译结果：</h3>
      <el-card class="box-card">
        <div class="translation-comparison">
          <div class="source-text">
            <h4>原文</h4>
            <p>{{ sourceText }}</p>
          </div>
          <div class="target-text">
            <h4>译文</h4>
            <p>{{ translationResult }}</p>
          </div>
        </div>
        <div style="margin-top: 10px;">
          <el-button type="success" @click="copyTranslation">复制译文</el-button>
          <el-button type="primary" @click="saveTranslation">保存对比</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

const sourceText = ref('');
const translationResult = ref('');

const translationOptions = reactive({
  targetLang: 'en',
  style: 'literal'
});

const translateText = () => {
  if (sourceText.value.trim() === '') {
    alert('请输入需要翻译的文本');
    return;
  }
  // 这里可以调用API接口进行翻译（示例留空）
  translationResult.value = 'This is the translated text (example).';
};

const copyTranslation = () => {
  if (translationResult.value) {
    navigator.clipboard.writeText(translationResult.value)
      .then(() => alert('译文已复制到剪贴板'))
      .catch(err => console.error('复制失败:', err));
  }
};

const saveTranslation = () => {
  // 这里可以实现保存翻译对比的功能
  alert('保存功能开发中...');
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
.translation-options {
  max-width: 600px;
  margin: 0 auto;
}
.translation-comparison {
  display: flex;
  gap: 20px;
}
.source-text, .target-text {
  flex: 1;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
h4 {
  margin-top: 0;
  color: #409EFF;
}
.box-card {
 