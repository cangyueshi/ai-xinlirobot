<template>
  <view class="page">
    <view class="page-header">
      <text class="page-back" @click="uni.navigateBack">&larr;</text>
      <view class="page-header-body">
        <text class="page-title">选择咨询师</text>
        <text class="page-subtitle">请选择你希望预约的咨询师</text>
      </view>
    </view>

    <!-- 前置条件检查 -->
    <view v-if="prereqChecked && !prereqReady" class="prereq-bar">
      <view class="prereq-dot"></view>
      <view class="prereq-body">
        <text class="prereq-title">完成测评后再预约</text>
        <text class="prereq-desc">请先完成 GAD-7 和 PHQ-9 量表评估</text>
      </view>
      <text class="prereq-link" @click="goAssessment">去完成</text>
    </view>

    <view v-if="loading" class="loading-state">
      <view class="loading-ring"></view>
      <text class="loading-label">加载中...</text>
    </view>

    <view v-else-if="counselors.length === 0" class="empty-state">
      <view class="empty-icon-wrap">
        <text class="empty-icon-symbol">&hearts;</text>
      </view>
      <text class="empty-title">暂无可预约的咨询师</text>
      <text class="empty-desc">请稍后再来查看</text>
    </view>

    <view class="counselor-list">
      <view
        v-for="c in counselors"
        :key="c.id"
        class="counselor-card"
        @click="selectCounselor(c)"
      >
        <view class="card-avatar" :style="{ background: avatarColor(c.display_name) }">
          <text class="card-avatar-text">{{ c.display_name.charAt(0) }}</text>
        </view>
        <view class="card-main">
          <text class="card-name">{{ c.display_name }}</text>
          <text v-if="c.specialties" class="card-tags">{{ c.specialties }}</text>
          <text v-if="c.bio" class="card-bio">{{ c.bio }}</text>
        </view>
        <text class="card-arrow">&rsaquo;</text>
      </view>
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

const avatarColors = ["#D4956A", "#A6A08C", "#90A8B0", "#B89A9A", "#C4A87A"];

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
// ====================================================
//  Warm Amber - 咨询师选择
// ====================================================
$bg-main:       #FDF8F4;
$bg-card:       #FFFFFF;
$primary:       #D4956A;
$primary-dark:  #B87A52;
$primary-light: #F0DCC8;
$primary-pale:  #F8EDE2;

$text-primary:  #3D322A;
$text-secondary:#8A8275;
$text-muted:    #B5A99A;

$border-soft:   #E8E0D0;
$shadow-card:   0 2px 12px rgba(61, 50, 42, 0.05);

$radius-card:   20px;
$radius-item:   16px;
$font-stack:    -apple-system, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;

.page {
  min-height: 100vh;
  background: $bg-main;
  padding: 0 20px 20px;
  font-family: $font-stack;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 0 16px;
}

.page-back {
  font-size: 24px;
  color: $text-primary;
  padding: 4px;
  cursor: pointer;
  font-weight: 300;
  line-height: 1;
}

.page-back:active {
  opacity: 0.6;
}

.page-header-body {
  flex: 1;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: $text-primary;
  display: block;
  letter-spacing: 0.01em;
}

.page-subtitle {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-top: 3px;
}

//  前置条件
.prereq-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #FBF5E8;
  border: 1px solid #E8DCC8;
  border-radius: $radius-item;
  padding: 14px 16px;
  margin-bottom: 16px;
}

.prereq-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #D4A76A;
  flex-shrink: 0;
}

.prereq-body {
  flex: 1;
}

.prereq-title {
  font-size: 13px;
  font-weight: 600;
  color: #A0853A;
  display: block;
  margin-bottom: 2px;
}

.prereq-desc {
  font-size: 12px;
  color: #B8A06A;
  display: block;
  line-height: 1.4;
}

.prereq-link {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: #D4A76A;
  padding: 6px 16px;
  border-radius: 30px;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}

.prereq-link:active {
  opacity: 0.85;
}

//  空状态
.loading-state {
  text-align: center;
  padding: 80px 0;
}

.loading-ring {
  width: 32px;
  height: 32px;
  border: 3px solid $border-soft;
  border-top-color: $primary;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}

.loading-label {
  font-size: 13px;
  color: $text-muted;
}

.empty-state {
  text-align: center;
  padding: 80px 0;
}

.empty-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: $primary-pale;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
}

.empty-icon-symbol {
  font-size: 22px;
  color: $primary;
}

.empty-title {
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 4px;
}

.empty-desc {
  font-size: 13px;
  color: $text-muted;
  display: block;
}

//  咨询师卡片
.counselor-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.counselor-card {
  display: flex;
  align-items: center;
  background: $bg-card;
  padding: 18px;
  border-radius: $radius-card;
  box-shadow: $shadow-card;
  transition: all 0.15s ease;
  cursor: pointer;
  border: 1px solid transparent;
}

.counselor-card:active {
  transform: scale(0.98);
  border-color: $primary-light;
}

.card-avatar {
  width: 50px;
  height: 50px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}

.card-avatar-text {
  font-size: 20px;
  color: #fff;
  font-weight: 700;
}

.card-main {
  flex: 1;
}

.card-name {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 4px;
}

.card-tags {
  font-size: 12px;
  color: $primary;
  display: block;
  margin-bottom: 3px;
  font-weight: 500;
}

.card-bio {
  font-size: 12px;
  color: $text-secondary;
  display: block;
  line-height: 1.4;
}

.card-arrow {
  font-size: 24px;
  color: $text-muted;
  margin-left: 8px;
  font-weight: 300;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
