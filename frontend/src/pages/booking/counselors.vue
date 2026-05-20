<template>
  <view class="page">
    <view class="header">
      <text class="page-title">选择咨询师</text>
      <text class="page-desc">请选择你希望预约的咨询师</text>
    </view>

    <!-- 前置条件检查 -->
    <view v-if="prereqChecked && !prereqReady" class="prereq-bar">
      <text class="prereq-icon">📝</text>
      <view class="prereq-info">
        <text class="prereq-title">预约前需先完成心理测评</text>
        <text class="prereq-desc">请先完成 GAD-7 和 PHQ-9 量表评估</text>
      </view>
      <text class="prereq-arrow" @click="goAssessment">去测评 ›</text>
    </view>

    <view v-if="loading" class="loading">
      <text class="loading-text">加载中...</text>
    </view>

    <view v-else-if="counselors.length === 0" class="empty">
      <text class="empty-icon">👩‍⚕️</text>
      <text class="empty-text">暂无可预约的咨询师</text>
    </view>

    <view
      v-for="c in counselors"
      :key="c.id"
      class="card"
      @click="selectCounselor(c)"
    >
      <view class="card-avatar" :style="{ background: avatarColor(c.display_name) }">
        <text class="card-avatar-text">{{ c.display_name.charAt(0) }}</text>
      </view>
      <view class="card-body">
        <text class="card-name">{{ c.display_name }}</text>
        <text v-if="c.specialties" class="card-tags">{{ c.specialties }}</text>
        <text v-if="c.bio" class="card-bio">{{ c.bio }}</text>
      </view>
      <text class="card-arrow">›</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getCounselors, checkPrerequisites, type Counselor } from "@/api/appointment";

const counselors = ref<Counselor[]>([]);
const loading = ref(true);
const prereqChecked = ref(false);
const prereqReady = ref(false);

const avatarColors = ["#5b8c7e", "#c97b63", "#6b9ac4", "#b88cb0", "#d4a56a"];

function avatarColor(name: string) {
  return avatarColors[name.charCodeAt(0) % avatarColors.length];
}

onMounted(async () => {
  try {
    const [prereq, list] = await Promise.all([
      checkPrerequisites(),
      getCounselors(),
    ]);
    prereqChecked.value = true;
    prereqReady.value = prereq.ready;
    counselors.value = list;
  } catch {
    uni.showToast({ title: "加载失败", icon: "none" });
  } finally {
    loading.value = false;
  }
});

function selectCounselor(c: Counselor) {
  if (!prereqReady.value) {
    uni.showModal({
      title: "测评未完成",
      content: "预约前请先完成 GAD-7 和 PHQ-9 心理测评",
      confirmText: "去测评",
      success: (res) => {
        if (res.confirm) goAssessment();
      },
    });
    return;
  }
  uni.navigateTo({
    url: `/pages/booking/select?counselorId=${c.id}&name=${encodeURIComponent(c.display_name)}`,
  });
}

function goAssessment() {
  uni.navigateTo({ url: '/pages/assessment/list' });
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
  margin-bottom: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: $text-primary;
  display: block;
}

.page-desc {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-top: 4px;
}

.prereq-bar {
  display: flex;
  align-items: center;
  background: #fff8e6;
  border: 1px solid #f0d78c;
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 16px;
}

.prereq-icon {
  font-size: 24px;
  margin-right: 10px;
}

.prereq-info {
  flex: 1;
}

.prereq-title {
  font-size: 14px;
  font-weight: 600;
  color: #b8860b;
  display: block;
}

.prereq-desc {
  font-size: 12px;
  color: #a0853a;
  display: block;
  margin-top: 2px;
}

.prereq-arrow {
  font-size: 13px;
  color: #b8860b;
  font-weight: 500;
}

.loading {
  text-align: center;
  padding: 60px 0;
}

.loading-text {
  font-size: 14px;
  color: $text-muted;
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
  display: flex;
  align-items: center;
  background: $card-bg;
  padding: 16px;
  border-radius: 16px;
  margin-bottom: 10px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}

.card:active {
  transform: scale(0.98);
}

.card-avatar {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 14px;
  flex-shrink: 0;
}

.card-avatar-text {
  font-size: 20px;
  color: #fff;
  font-weight: 700;
}

.card-body {
  flex: 1;
}

.card-name {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
  display: block;
}

.card-tags {
  font-size: 12px;
  color: $primary;
  display: block;
  margin-top: 4px;
}

.card-bio {
  font-size: 12px;
  color: $text-secondary;
  display: block;
  margin-top: 2px;
  line-height: 1.4;
}

.card-arrow {
  font-size: 22px;
  color: #d0d5d5;
  margin-left: 8px;
}
</style>
