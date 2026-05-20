<template>
  <view class="page">
    <!-- 未通过审核提示 -->
    <view v-if="!isApproved" class="pending-banner">
      <text class="pending-icon">⏳</text>
      <view class="pending-body">
        <text class="pending-title">账号审核中</text>
        <text class="pending-desc">你的账号尚未通过管理员审核，审核通过前来访者无法看到你的信息。请耐心等待管理员审核。</text>
      </view>
    </view>

    <view class="header">
      <text class="greeting">{{ userStore.userInfo?.display_name || '咨询师' }}，早上好</text>
      <text class="greeting-sub">今天有 {{ data.upcoming_appointments }} 个待处理预约</text>
    </view>

    <!-- 核心数据 -->
    <view class="stats-row">
      <view class="stat-card" @click="goPage('/pages/appointments/list')">
        <text class="stat-num warn">{{ data.upcoming_appointments }}</text>
        <text class="stat-label">待处理预约</text>
      </view>
      <view
        class="stat-card"
        :class="data.unread_alerts > 0 ? 'pulse' : ''"
        @click="goPage('/pages/chat/alerts')"
      >
        <text class="stat-num" :class="data.unread_alerts > 0 ? 'danger' : 'muted'">
          {{ data.unread_alerts }}
        </text>
        <text class="stat-label">未读预警</text>
      </view>
      <view class="stat-card" @click="goPage('/pages/counselor/visitors')">
        <text class="stat-num primary">{{ data.total_visitors }}</text>
        <text class="stat-label">来访者</text>
      </view>
      <view class="stat-card">
        <text class="stat-num accent">{{ data.total_chat_sessions }}</text>
        <text class="stat-label">已完成对话</text>
      </view>
    </view>

    <!-- 最近对话 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">最近对话</text>
        <text class="section-more" @click="goPage('/pages/counselor/visitors')">查看全部 ›</text>
      </view>
      <view v-if="(data.recent_sessions?.length || 0) === 0" class="empty">
        <text class="empty-text">暂无最近对话</text>
      </view>
      <view
        v-for="s in data.recent_sessions"
        :key="s.id"
        class="session-card"
        @click="viewSession(s)"
      >
        <view class="session-top">
          <view class="session-tags">
            <text class="tag-risk" :class="s.risk_level">
              {{ riskLabel(s.risk_level) }}
            </text>
            <text class="session-id">ID {{ s.id }}</text>
          </view>
          <text class="session-time">{{ fmtTime(s.updated_at) }}</text>
        </view>
        <text class="session-summary">{{ s.ai_summary || '暂无摘要' }}</text>
        <text class="session-visitor" v-if="s.visitor_id">
          来访者 ID: {{ s.visitor_id }}
        </text>
      </view>
    </view>

    <!-- 快捷操作 -->
    <view class="quick-actions">
      <view class="quick-btn" @click="goPage('/pages/availability/manage')">
        <text class="quick-icon">⏰</text>
        <text class="quick-label">排班管理</text>
      </view>
      <view class="quick-btn" @click="goPage('/pages/counselor/visitors')">
        <text class="quick-icon">👥</text>
        <text class="quick-label">来访者中心</text>
      </view>
      <view class="quick-btn" @click="goPage('/pages/chat/alerts')">
        <text class="quick-icon">🔔</text>
        <text class="quick-label">风险预警</text>
      </view>
      <view class="quick-btn" @click="goPage('/pages/appointments/list')">
        <text class="quick-icon">📋</text>
        <text class="quick-label">预约管理</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getDashboard } from "@/api/counselor";
import { useUserStore } from "@/store/user";

const userStore = useUserStore();
const isApproved = computed(() => userStore.userInfo?.is_approved !== false);

const data = ref<any>({
  upcoming_appointments: 0,
  unread_alerts: 0,
  total_visitors: 0,
  total_chat_sessions: 0,
  recent_sessions: [],
});

onMounted(async () => {
  try {
    data.value = await getDashboard();
  } catch {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
});

function riskLabel(l: string) {
  return l === "red" ? "高危" : l === "yellow" ? "中度" : "正常";
}

function fmtTime(t: string | null) {
  if (!t) return "";
  return t.slice(0, 16).replace("T", " ");
}

function goPage(url: string) {
  uni.navigateTo({ url });
}

function viewSession(s: any) {
  uni.navigateTo({
    url: `/pages/chat/detail?id=${s.id}&visitorId=${s.visitor_id}`,
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

.pending-banner {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #fdf6ec;
  border: 1px solid #f0d78c;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 16px;
}

.pending-icon {
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 1px;
}

.pending-body {
  flex: 1;
}

.pending-title {
  font-size: 14px;
  font-weight: 600;
  color: #b8860b;
  display: block;
  margin-bottom: 4px;
}

.pending-desc {
  font-size: 12px;
  color: #a0853a;
  line-height: 1.5;
  display: block;
}

.header {
  margin-bottom: 20px;
}

.greeting {
  font-size: 22px;
  font-weight: 700;
  color: $text-primary;
  display: block;
}

.greeting-sub {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-top: 4px;
}

.stats-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 20px;
}

.stat-card {
  background: $card-bg;
  padding: 16px 12px;
  border-radius: 14px;
  text-align: center;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}

.stat-num {
  font-size: 28px;
  font-weight: 700;
  display: block;
  margin-bottom: 2px;
}

.stat-num.warn { color: #e6a23c; }
.stat-num.danger { color: #f56c6c; }
.stat-num.primary { color: $primary; }
.stat-num.accent { color: #6b9ac4; }
.stat-num.muted { color: $text-muted; }

.stat-label {
  font-size: 12px;
  color: $text-muted;
}

.pulse {
  animation: subtlePulse 2s infinite;
}

@keyframes subtlePulse {
  0%, 100% { box-shadow: 0 1px 6px rgba(0,0,0,0.04); }
  50% { box-shadow: 0 1px 10px rgba(245,108,108,0.15); }
}

.section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: $text-primary;
}

.section-more {
  font-size: 13px;
  color: $primary;
}

.empty {
  text-align: center;
  padding: 30px 0;
}

.empty-text {
  font-size: 14px;
  color: $text-muted;
}

.session-card {
  background: $card-bg;
  padding: 14px 16px;
  border-radius: 14px;
  margin-bottom: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

.session-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.session-tags {
  display: flex;
  gap: 6px;
  align-items: center;
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

.session-id {
  font-size: 11px;
  color: $text-muted;
}

.session-time {
  font-size: 11px;
  color: $text-muted;
}

.session-summary {
  font-size: 13px;
  color: $text-secondary;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.session-visitor {
  font-size: 11px;
  color: $text-muted;
  margin-top: 6px;
  display: block;
}

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.quick-btn {
  background: $card-bg;
  padding: 14px 8px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

.quick-btn:active {
  transform: scale(0.97);
}

.quick-icon {
  font-size: 22px;
  display: block;
  margin-bottom: 4px;
}

.quick-label {
  font-size: 13px;
  color: $text-primary;
  font-weight: 500;
}
</style>
