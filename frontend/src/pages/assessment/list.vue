<template>
  <view class="page">
    <view class="header">
      <text class="page-title">心理测评</text>
      <text class="page-desc">选择量表进行心理健康自评，结果仅对你和咨询师可见</text>
    </view>

    <!-- 预约提醒 -->
    <view class="info-bar">
      <text class="info-bar-icon">📌</text>
      <text class="info-bar-text">预约咨询师前需先完成「GAD-7 焦虑评估」和「PHQ-9 抑郁评估」</text>
    </view>

    <view v-if="scales.length === 0" class="empty">
      <text class="empty-icon">📝</text>
      <text class="empty-text">暂无可用量表</text>
    </view>

    <view
      v-for="s in scales"
      :key="s.id"
      class="card"
      :class="{ required: isRequired(s.name) }"
      @click="startScale(s)"
    >
      <view class="card-top">
        <text class="card-title">{{ s.name }}</text>
        <text v-if="isRequired(s.name)" class="required-tag">预约必备</text>
        <text v-else class="optional-tag">选做</text>
      </view>
      <text class="card-desc">{{ s.description }}</text>
      <view class="card-footer">
        <text class="card-count">共 {{ s.question_count }} 题</text>
        <text class="card-action">开始测评 →</text>
      </view>
    </view>

    <view class="link-row" @click="goHistory">
      <text class="link-text">查看历史测评记录 →</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getScales, type Scale } from "@/api/assessment";

const scales = ref<Scale[]>([]);
const REQUIRED_NAMES = ["GAD-7 焦虑症筛查量表", "PHQ-9 抑郁症筛查量表"];

function isRequired(name: string) {
  return REQUIRED_NAMES.includes(name);
}

onMounted(async () => {
  try {
    scales.value = await getScales();
  } catch {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
});

function startScale(s: Scale) {
  uni.navigateTo({
    url: `/pages/assessment/answer?scaleId=${s.id}&name=${encodeURIComponent(s.name)}`,
  });
}

function goHistory() {
  uni.navigateTo({ url: "/pages/assessment/history" });
}
</script>

<style lang="scss" scoped>
$bg: #f5f3ef;
$card-bg: #ffffff;
$primary: #5b8c7e;
$text-primary: #2c3e50;
$text-secondary: #7a8a8a;
$text-muted: #aab7b7;

.page {
  padding: 16px;
  min-height: 100vh;
  background: $bg;
}

.header {
  margin-bottom: 12px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: $text-primary;
  display: block;
}

.page-desc {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-top: 4px;
  line-height: 1.5;
}

.info-bar {
  display: flex;
  align-items: flex-start;
  background: #f0f7f4;
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 16px;
  gap: 8px;
}

.info-bar-icon {
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 1px;
}

.info-bar-text {
  font-size: 12px;
  color: $primary;
  line-height: 1.5;
}

.empty {
  text-align: center;
  padding: 60px 0;
}

.empty-icon {
  font-size: 40px;
  display: block;
  margin-bottom: 10px;
}

.empty-text {
  font-size: 14px;
  color: $text-muted;
}

.card {
  background: $card-bg;
  padding: 18px;
  border-radius: 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04);
  border-left: 4px solid transparent;
}

.card.required {
  border-left-color: $primary;
}

.card-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
  flex: 1;
}

.required-tag {
  font-size: 10px;
  color: #fff;
  background: $primary;
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 500;
}

.optional-tag {
  font-size: 10px;
  color: $text-muted;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 6px;
}

.card-desc {
  font-size: 13px;
  color: $text-secondary;
  line-height: 1.5;
  display: block;
  margin-bottom: 12px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-count {
  font-size: 12px;
  color: $text-muted;
}

.card-action {
  font-size: 14px;
  color: $primary;
  font-weight: 500;
}

.link-row {
  text-align: center;
  padding: 16px 0;
}

.link-text {
  font-size: 14px;
  color: $primary;
}
</style>
