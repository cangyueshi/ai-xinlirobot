<template>
  <view class="page">
    <view class="header">
      <text class="page-title">来访者信息中心</text>
      <text class="page-count">共 {{ visitors.length }} 人</text>
    </view>

    <view v-if="visitors.length === 0" class="empty">
      <text class="empty-icon">👥</text>
      <text class="empty-text">暂无来访者</text>
    </view>

    <view v-for="v in visitors" :key="v.id" class="card" @click="viewVisitor(v)">
      <view class="card-left">
        <view class="avatar" :style="{ background: avatarColor(v.display_name) }">
          <text class="avatar-text">{{ v.display_name.charAt(0) }}</text>
        </view>
      </view>
      <view class="card-body">
        <view class="card-top">
          <text class="card-name">{{ v.display_name }}</text>
          <text class="card-id">ID: {{ v.id }}</text>
        </view>
        <text class="card-phone">{{ v.phone || '未留电话' }}</text>
        <view class="card-stats">
          <view class="stat">
            <text class="stat-num">{{ v.chat_count }}</text>
            <text class="stat-label">次对话</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat">
            <text class="stat-num">{{ v.assessment_count }}</text>
            <text class="stat-label">次测评</text>
          </view>
        </view>
      </view>
      <text class="card-arrow">›</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getAllVisitors, type VisitorInfo } from "@/api/counselor";

const visitors = ref<VisitorInfo[]>([]);

onMounted(async () => {
  try {
    visitors.value = await getAllVisitors();
  } catch {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
});

const avatarColors = ["#5b8c7e", "#c97b63", "#6b9ac4", "#b88cb0", "#d4a56a", "#7aa89e"];

function avatarColor(name: string) {
  const idx = name.charCodeAt(0) % avatarColors.length;
  return avatarColors[idx];
}

function viewVisitor(v: VisitorInfo) {
  uni.navigateTo({
    url: `/pages/counselor/visitorDetail?id=${v.id}&name=${encodeURIComponent(v.display_name)}`,
  });
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
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: $text-primary;
}

.page-count {
  font-size: 13px;
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
  transition: transform 0.15s;
}

.card:active {
  transform: scale(0.98);
}

.card-left {
  margin-right: 14px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 20px;
  color: #fff;
  font-weight: 700;
}

.card-body {
  flex: 1;
}

.card-top {
  display: flex;
  align-items: center;
  margin-bottom: 2px;
}

.card-name {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
}

.card-id {
  font-size: 11px;
  color: $text-muted;
  margin-left: 8px;
  background: #f0f0f0;
  padding: 1px 6px;
  border-radius: 4px;
}

.card-phone {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-bottom: 8px;
}

.card-stats {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat {
  display: flex;
  align-items: baseline;
  gap: 3px;
}

.stat-num {
  font-size: 15px;
  font-weight: 700;
  color: $primary;
}

.stat-label {
  font-size: 11px;
  color: $text-muted;
}

.stat-divider {
  width: 1px;
  height: 14px;
  background: #e0e0e0;
}

.card-arrow {
  font-size: 22px;
  color: #d0d5d5;
  margin-left: 8px;
}
</style>
