<template>
  <view class="container">
    <text class="page-title">管理后台</text>

    <view class="stat-grid">
      <view class="stat-card">
        <text class="stat-num">{{ stats.total_visitors }}</text>
        <text class="stat-label">来访者</text>
      </view>
      <view class="stat-card">
        <text class="stat-num">{{ stats.total_counselors }}</text>
        <text class="stat-label">咨询师</text>
      </view>
      <view class="stat-card">
        <text class="stat-num">{{ stats.total_sessions }}</text>
        <text class="stat-label">总对话</text>
      </view>
      <view class="stat-card">
        <text class="stat-num">{{ stats.active_sessions }}</text>
        <text class="stat-label">进行中</text>
      </view>
    </view>

    <view class="section">
      <text class="section-title">数据导出</text>
      <view class="export-list">
        <view class="export-item" @click="doExport('visitors')">
          <text>导出访客数据 (CSV)</text><text class="arrow">›</text>
        </view>
        <view class="export-item" @click="doExport('counselors')">
          <text>导出咨询师数据 (CSV)</text><text class="arrow">›</text>
        </view>
        <view class="export-item" @click="doExport('chat-sessions')">
          <text>导出对话会话 (CSV)</text><text class="arrow">›</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getDashboard, exportVisitors, exportCounselors, exportChatSessions } from "@/api/admin";

const stats = ref({ total_visitors: 0, total_counselors: 0, total_sessions: 0, active_sessions: 0 });

onMounted(async () => {
  try {
    stats.value = await getDashboard();
  } catch (e) {}
});

async function doExport(type: string) {
  try {
    if (type === "visitors") await exportVisitors();
    else if (type === "counselors") await exportCounselors();
    else await exportChatSessions();
    uni.showToast({ title: "导出成功", icon: "success" });
  } catch (e) {
    uni.showToast({ title: "导出失败", icon: "none" });
  }
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.page-title { font-size: 20px; font-weight: bold; color: #303133; margin-bottom: 16px; display: block; }
.stat-grid { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.stat-card {
  flex: 1; min-width: 80px; background: #fff; border-radius: 10px;
  padding: 16px 12px; text-align: center;
}
.stat-num { font-size: 28px; font-weight: bold; color: #409eff; display: block; }
.stat-label { font-size: 12px; color: #909399; margin-top: 4px; }
.section { background: #fff; border-radius: 10px; padding: 16px; margin-bottom: 14px; }
.section-title { font-size: 16px; font-weight: bold; color: #303133; display: block; margin-bottom: 12px; }
.export-item { display: flex; justify-content: space-between; padding: 14px 0; border-bottom: 1px solid #f0f0f0; font-size: 14px; color: #303133; }
.arrow { color: #c0c4cc; font-size: 18px; }
</style>