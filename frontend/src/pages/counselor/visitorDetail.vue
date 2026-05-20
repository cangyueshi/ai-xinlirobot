<template>
  <view class="page">
    <!-- 来访者信息头 -->
    <view class="profile-card">
      <view class="profile-avatar" :style="{ background: avatarColor }">
        <text class="profile-avatar-text">{{ initial }}</text>
      </view>
      <view class="profile-info">
        <text class="profile-name">{{ visitorName }}</text>
        <text class="profile-id">来访者 ID: {{ visitorId }}</text>
        <text class="profile-phone">{{ visitorPhone || '未留电话' }}</text>
      </view>
    </view>

    <!-- 概览卡片 -->
    <view class="overview-row">
      <view class="overview-card">
        <text class="overview-num">{{ sessions.length }}</text>
        <text class="overview-label">对话次数</text>
      </view>
      <view class="overview-card">
        <text class="overview-num">{{ assessments.length }}</text>
        <text class="overview-label">测评次数</text>
      </view>
      <view class="overview-card">
        <text class="overview-num">{{ highRiskCount }}</text>
        <text class="overview-label">高危预警</text>
      </view>
    </view>

    <!-- Tab 切换 -->
    <view class="tabs">
      <view
        class="tab"
        :class="{ active: tab === 'chat' }"
        @click="tab = 'chat'"
      >💬 对话记录</view>
      <view
        class="tab"
        :class="{ active: tab === 'assessment' }"
        @click="tab = 'assessment'"
      >📝 测评记录</view>
    </view>

    <!-- 对话记录 -->
    <view v-if="tab === 'chat'">
      <view v-if="sessions.length === 0" class="empty">暂无对话记录</view>
      <view
        v-for="s in sessions"
        :key="s.id"
        class="record-card"
        @click="viewChat(s)"
      >
        <view class="record-header">
          <view class="record-tags">
            <text class="tag-risk" :class="s.risk_level">
              {{ riskLabel(s.risk_level) }}
            </text>
            <text class="tag-status">{{ s.status === 'completed' ? '已结束' : '进行中' }}</text>
          </view>
          <text class="record-time">{{ fmtTime(s.created_at) }}</text>
        </view>
        <view class="record-id-row">
          <text class="record-id-label">对话 ID:</text>
          <text class="record-id-val">{{ s.id }}</text>
          <text class="record-duration" v-if="s.user_message_count">
            {{ s.user_message_count }} 条消息
          </text>
        </view>
        <text class="record-summary">{{ s.ai_summary || '暂无摘要' }}</text>
      </view>
    </view>

    <!-- 测评记录 -->
    <view v-if="tab === 'assessment'">
      <view v-if="assessments.length === 0" class="empty">暂无测评记录</view>
      <view
        v-for="a in assessments"
        :key="a.id"
        class="record-card"
      >
        <view class="record-header">
          <text class="scale-name">{{ a.scale_name }}</text>
          <text class="tag-risk" :class="a.result_level">
            {{ riskLabel(a.result_level) }}
          </text>
        </view>
        <text class="score-text">
          总分 {{ a.total_score }}
          <text v-if="a.result_detail" class="score-detail">
            · {{ a.result_detail.split('|').pop()?.trim() || '' }}
          </text>
        </text>
        <text class="record-time">{{ fmtTime(a.created_at) }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { getVisitorSessions, getVisitorAssessments } from "@/api/counselor";

const visitorId = ref(0);
const visitorName = ref("");
const visitorPhone = ref("");
const tab = ref("chat");
const sessions = ref<any[]>([]);
const assessments = ref<any[]>([]);

const initial = computed(() => visitorName.value.charAt(0) || "?");

const avatarColors = ["#5b8c7e", "#c97b63", "#6b9ac4", "#b88cb0", "#d4a56a", "#7aa89e"];
const avatarColor = computed(() => {
  const idx = (visitorName.value.charCodeAt(0) || 0) % avatarColors.length;
  return avatarColors[idx];
});

const highRiskCount = computed(() =>
  sessions.value.filter((s) => s.risk_level === "red").length
);

onMounted(async () => {
  const pages = getCurrentPages();
  const opts = (pages[pages.length - 1].options as any);
  visitorId.value = Number(opts.id);
  visitorName.value = decodeURIComponent(opts.name || "");

  try {
    [sessions.value, assessments.value] = await Promise.all([
      getVisitorSessions(visitorId.value),
      getVisitorAssessments(visitorId.value),
    ]);
  } catch {}
});

function riskLabel(l: string) {
  return l === "red" ? "高危" : l === "yellow" ? "中度" : "正常";
}

function fmtTime(t: string | null) {
  if (!t) return "";
  return t.slice(0, 16).replace("T", " ");
}

function viewChat(s: any) {
  uni.navigateTo({ url: `/pages/chat/detail?id=${s.id}&visitorId=${visitorId.value}&visitorName=${encodeURIComponent(visitorName.value)}` });
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

.profile-card {
  display: flex;
  align-items: center;
  background: $card-bg;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 12px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}

.profile-avatar {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}

.profile-avatar-text {
  font-size: 24px;
  color: #fff;
  font-weight: 700;
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 18px;
  font-weight: 700;
  color: $text-primary;
  display: block;
}

.profile-id {
  font-size: 12px;
  color: $text-muted;
  display: block;
  margin-top: 2px;
}

.profile-phone {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-top: 4px;
}

.overview-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.overview-card {
  flex: 1;
  background: $card-bg;
  border-radius: 12px;
  padding: 14px 8px;
  text-align: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

.overview-num {
  font-size: 24px;
  font-weight: 700;
  color: $primary;
  display: block;
}

.overview-label {
  font-size: 11px;
  color: $text-muted;
  display: block;
  margin-top: 2px;
}

.tabs {
  display: flex;
  background: $card-bg;
  border-radius: 12px;
  margin-bottom: 12px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

.tab {
  flex: 1;
  text-align: center;
  padding: 12px 0;
  font-size: 13px;
  color: $text-muted;
  transition: all 0.2s;
}

.tab.active {
  color: $primary;
  font-weight: 600;
  border-bottom: 2px solid $primary;
}

.empty {
  text-align: center;
  color: $text-muted;
  padding: 40px 0;
  font-size: 14px;
}

.record-card {
  background: $card-bg;
  padding: 14px 16px;
  border-radius: 14px;
  margin-bottom: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.record-tags {
  display: flex;
  gap: 6px;
}

.tag-risk {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}
.tag-risk.red { color: #f56c6c; background: #fef0f0; }
.tag-risk.yellow { color: #e6a23c; background: #fdf6ec; }
.tag-risk.none { color: #67c23a; background: #f0f9eb; }

.tag-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  color: #909399;
  background: #f5f5f5;
}

.record-time {
  font-size: 11px;
  color: $text-muted;
}

.record-id-row {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 6px;
}

.record-id-label {
  font-size: 11px;
  color: $text-muted;
}

.record-id-val {
  font-size: 11px;
  color: $text-secondary;
  font-family: monospace;
}

.record-duration {
  font-size: 11px;
  color: $text-muted;
  margin-left: auto;
}

.record-summary {
  font-size: 13px;
  color: $text-secondary;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.scale-name {
  font-size: 14px;
  color: $text-primary;
  font-weight: 500;
}

.score-text {
  font-size: 14px;
  color: $text-primary;
  display: block;
  margin: 4px 0;
}

.score-detail {
  color: $text-secondary;
  font-size: 13px;
}
</style>
