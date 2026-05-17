<template>
  <view class="container">
    <view class="result-card" :class="levelClass">
      <text class="scale-name">{{ result.scale_name }}</text>
      <text class="score">{{ result.total_score }} 分</text>
      <text class="level-label">{{ result.result_label }}</text>
    </view>

    <view class="info-card">
      <text class="info-title">结果说明</text>
      <text class="info-text" v-if="result.result_level === 'none'">
        您的自评结果在正常范围内。如果仍有困扰，欢迎随时与AI对话或预约咨询师沟通。
      </text>
      <text class="info-text" v-if="result.result_level === 'yellow'">
        您的自评结果显示可能存在一定程度的心理困扰。建议与咨询师进一步沟通评估，您可以通过平台的AI对话功能先聊聊感受。
      </text>
      <text class="info-text warning" v-if="result.result_level === 'red'">
        您的自评结果显示需要引起关注。请尽快与咨询师沟通。如果您有伤害自己的想法，请立即拨打心理援助热线：希望24热线 400-161-9995。
      </text>
    </view>

    <view class="tip-card">
      <text class="tip-text">⚠️ 此测评仅为筛查工具，不能作为诊断依据。最终评估需由专业心理咨询师完成。</text>
    </view>

    <button class="back-btn" @click="goHome">返回首页</button>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

const result = ref<any>({ scale_name: "", total_score: 0, result_label: "", result_level: "none" });

onMounted(() => {
  const pages = getCurrentPages();
  const opts = (pages[pages.length - 1].options as any);
  if (opts.data) {
    result.value = JSON.parse(decodeURIComponent(opts.data));
  }
});

const levelClass = computed(() => {
  return "level-" + (result.value.result_level || "none");
});

function goHome() {
  uni.reLaunch({ url: "/pages/index/index" });
}
</script>

<style lang="scss" scoped>
.container { padding: 20px 16px; min-height: 100vh; background: #f5f5f5; }
.result-card { padding: 30px; border-radius: 16px; text-align: center; margin-bottom: 16px; }
.result-card.level-none { background: #f0f9eb; }
.result-card.level-yellow { background: #fdf6ec; }
.result-card.level-red { background: #fef0f0; }
.scale-name { font-size: 14px; display: block; margin-bottom: 12px; }
.level-none .scale-name { color: #67c23a; }
.level-yellow .scale-name { color: #e6a23c; }
.level-red .scale-name { color: #f56c6c; }
.score { font-size: 42px; font-weight: bold; display: block; margin-bottom: 8px; color: #303133; }
.level-label { font-size: 18px; font-weight: 500; color: #303133; }
.info-card { background: #fff; padding: 18px; border-radius: 12px; margin-bottom: 12px; }
.info-title { font-size: 15px; font-weight: bold; color: #303133; display: block; margin-bottom: 8px; }
.info-text { font-size: 14px; color: #606266; line-height: 1.7; }
.info-text.warning { color: #f56c6c; }
.tip-card { background: #fdf6ec; padding: 14px; border-radius: 8px; margin-bottom: 20px; }
.tip-text { font-size: 13px; color: #e6a23c; line-height: 1.6; }
.back-btn { width: 100%; height: 46px; line-height: 46px; background: #409eff; color: #fff; border-radius: 8px; font-size: 16px; border: none; }
</style>