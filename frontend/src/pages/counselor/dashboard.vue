<template>
  <view class="container">
    <text class="page-title">工作台</text>

    <view class="stats-grid">
      <view class="stat-card blue" @click="goPage('/pages/appointments/list')">
        <text class="stat-num">{{ data.upcoming_appointments }}</text>
        <text class="stat-label">待处理预约</text>
      </view>
      <view class="stat-card" :class="data.unread_alerts > 0 ? 'red' : 'green'" @click="goPage('/pages/chat/alerts')">
        <text class="stat-num">{{ data.unread_alerts }}</text>
        <text class="stat-label">未读预警</text>
      </view>
      <view class="stat-card green" @click="goPage('/pages/counselor/visitors')">
        <text class="stat-num">{{ data.total_visitors }}</text>
        <text class="stat-label">来访者总数</text>
      </view>
      <view class="stat-card purple">
        <text class="stat-num">{{ data.total_chat_sessions }}</text>
        <text class="stat-label">已完成对话</text>
      </view>
    </view>

    <view class="section">
      <text class="section-title">最近对话</text>
      <view v-if="data.recent_sessions?.length === 0" class="empty">暂无</view>
      <view
        v-for="s in data.recent_sessions"
        :key="s.id"
        class="session-item"
        @click="viewSession(s.id)"
      >
        <view class="s-header">
          <text class="s-tag" :class="s.risk_level">
            {{ riskLabel(s.risk_level) }}
          </text>
          <text class="s-time">{{ fmtTime(s.updated_at) }}</text>
        </view>
        <text class="s-summary">{{ s.ai_summary || '暂无摘要' }}</text>
      </view>
    </view>

    <view class="quick-actions">
      <view class="action-btn" @click="goPage('/pages/availability/manage')">
        <text>⏰ 管理可预约时间</text>
      </view>
      <view class="action-btn" @click="goPage('/pages/counselor/visitors')">
        <text>👥 来访者管理</text>
      </view>
      <view class="action-btn" @click="goPage('/pages/chat/alerts')">
        <text>🔔 风险预警</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getDashboard } from "@/api/counselor";

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
  } catch (e) {
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

function viewSession(id: number) {
  uni.navigateTo({ url: `/pages/chat/detail?id=${id}` });
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.page-title { font-size: 22px; font-weight: bold; color: #303133; margin-bottom: 16px; display: block; }
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 18px; }
.stat-card { background: #fff; padding: 16px; border-radius: 12px; text-align: center; }
.stat-card.blue { background: #ecf5ff; }
.stat-card.red { background: #fef0f0; }
.stat-card.green { background: #f0f9eb; }
.stat-card.purple { background: #f5f0ff; }
.stat-num { font-size: 30px; font-weight: bold; display: block; margin-bottom: 4px; }
.stat-card.blue .stat-num { color: #409eff; }
.stat-card.red .stat-num { color: #f56c6c; }
.stat-card.green .stat-num { color: #67c23a; }
.stat-card.purple .stat-num { color: #9b59b6; }
.stat-label { font-size: 12px; color: #909399; }
.section { margin-bottom: 16px; }
.section-title { font-size: 17px; font-weight: bold; color: #303133; margin-bottom: 10px; display: block; }
.empty { text-align: center; color: #909399; padding: 20px 0; font-size: 14px; }
.session-item { background: #fff; padding: 14px 16px; border-radius: 10px; margin-bottom: 8px; }
.s-header { display: flex; justify-content: space-between; margin-bottom: 4px; }
.s-tag { font-size: 12px; padding: 1px 8px; border-radius: 4px; }
.s-tag.red { color: #f56c6c; background: #fef0f0; }
.s-tag.yellow { color: #e6a23c; background: #fdf6ec; }
.s-tag.none { color: #67c23a; background: #f0f9eb; }
.s-time { font-size: 12px; color: #c0c4cc; }
.s-summary { font-size: 13px; color: #606266; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.quick-actions { display: flex; flex-direction: column; gap: 8px; }
.action-btn { background: #fff; padding: 15px; border-radius: 10px; text-align: center; font-size: 15px; color: #409eff; }
</style>