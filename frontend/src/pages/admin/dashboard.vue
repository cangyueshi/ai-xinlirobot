<template>
  <view class="page">
    <view class="header">
      <text class="greeting">管理后台</text>
      <text class="greeting-sub">{{ userStore.userInfo?.display_name }} · {{ roleLabel }}</text>
    </view>

    <view class="stats-grid">
      <view class="stat-card" @click="goPage('/pages/admin/visitors')">
        <text class="stat-num primary">{{ data.total_visitors }}</text>
        <text class="stat-label">来访者</text>
      </view>
      <view class="stat-card" @click="goPage('/pages/admin/counselors')">
        <text class="stat-num accent">{{ data.total_counselors }}</text>
        <text class="stat-label">咨询师</text>
      </view>
      <view v-if="data.pending_counselors > 0" class="stat-card" @click="goPage('/pages/admin/counselors')" style="background:#fef5e7;">
        <text class="stat-num" style="color:#e6a23c;">{{ data.pending_counselors }}</text>
        <text class="stat-label" style="color:#a0853a;">待审核</text>
      </view>
      <view class="stat-card">
        <text class="stat-num info">{{ data.total_sessions }}</text>
        <text class="stat-label">总对话</text>
      </view>
      <view class="stat-card">
        <text class="stat-num warn">{{ data.active_sessions }}</text>
        <text class="stat-label">进行中</text>
      </view>
    </view>

    <text class="section-title">快捷入口</text>
    <view class="quick-grid">
      <view class="quick-card" @click="goPage('/pages/admin/counselors')">
        <text class="quick-icon">👩‍⚕️</text>
        <text class="quick-label">咨询师管理</text>
      </view>
      <view class="quick-card" @click="goPage('/pages/admin/sub-admins')">
        <text class="quick-icon">👤</text>
        <text class="quick-label">次级管理员</text>
      </view>
      <view class="quick-card" @click="goPage('/pages/admin/visitors')">
        <text class="quick-icon">👥</text>
        <text class="quick-label">来访者管理</text>
      </view>
    </view>

    <view class="section">
      <text class="section-title">数据导出</text>
      <view class="export-list">
        <view class="export-item" @click="doExport('visitors')">
          <text>导出访客数据 (CSV)</text>
          <text class="export-arrow">›</text>
        </view>
        <view class="export-item" @click="doExport('counselors')">
          <text>导出咨询师数据 (CSV)</text>
          <text class="export-arrow">›</text>
        </view>
        <view class="export-item" @click="doExport('chat-sessions')">
          <text>导出对话会话 (CSV)</text>
          <text class="export-arrow">›</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { getDashboard, exportVisitors, exportCounselors, exportChatSessions } from "@/api/admin";
import { useUserStore } from "@/store/user";

const userStore = useUserStore();
const data = ref({ total_visitors: 0, total_counselors: 0, pending_counselors: 0, total_sessions: 0, active_sessions: 0 });

const roleLabel = computed(() => {
  const labels: Record<string, string> = {
    super_admin: "超级管理员",
    sub_admin: "次级管理员",
  };
  return labels[userStore.userInfo?.role || ""] || "";
});

onMounted(async () => {
  try { data.value = await getDashboard(); } catch {}
});

function goPage(url: string) {
  uni.navigateTo({ url });
}

async function doExport(type: string) {
  try {
    if (type === "visitors") await exportVisitors();
    else if (type === "counselors") await exportCounselors();
    else await exportChatSessions();
    uni.showToast({ title: "导出成功", icon: "success" });
  } catch {
    uni.showToast({ title: "导出失败", icon: "none" });
  }
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

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 24px;
}

.stat-card {
  background: $card-bg;
  padding: 18px 12px;
  border-radius: 14px;
  text-align: center;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}

.stat-num {
  font-size: 30px;
  font-weight: 700;
  display: block;
  margin-bottom: 2px;
}
.stat-num.primary { color: $primary; }
.stat-num.accent { color: #6b9ac4; }
.stat-num.info { color: #409eff; }
.stat-num.warn { color: #e6a23c; }

.stat-label {
  font-size: 12px;
  color: $text-muted;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 12px;
}

.quick-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  margin-bottom: 24px;
}

.quick-card {
  background: $card-bg;
  padding: 20px 12px;
  border-radius: 14px;
  text-align: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

.quick-card:active {
  transform: scale(0.97);
}

.quick-icon {
  font-size: 28px;
  display: block;
  margin-bottom: 6px;
}

.quick-label {
  font-size: 13px;
  color: $text-primary;
  font-weight: 500;
}

.section {
  background: $card-bg;
  border-radius: 14px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

.export-list {
  margin-top: 4px;
}

.export-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  font-size: 14px;
  color: $text-primary;
}

.export-item + .export-item {
  border-top: 1px solid #f0f0f0;
}

.export-arrow {
  color: $text-muted;
  font-size: 18px;
}
</style>
