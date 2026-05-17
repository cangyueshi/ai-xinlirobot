<template>
  <view class="container">
    <text class="page-title">风险预警</text>

    <view v-if="alerts.length === 0" class="empty">暂无预警通知</view>

    <view
      v-for="a in alerts"
      :key="a.id"
      class="card"
      :class="{ unread: !a.is_read }"
      @click="viewAlert(a)"
    >
      <view class="header">
        <text class="level-tag" :class="a.level">
          {{ a.level === "red" ? "🔴 高危" : "🟡 中度" }}
        </text>
        <text class="time">{{ formatDate(a.created_at) }}</text>
        <view v-if="!a.is_read" class="dot"></view>
      </view>
      <text class="summary-text">{{ a.summary }}</text>
      <text class="action">查看对话记录 ›</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getAlerts, markAlertRead } from "@/api/chat";

const alerts = ref<any[]>([]);

onMounted(async () => {
  try {
    alerts.value = await getAlerts();
  } catch (e) {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
});

function formatDate(d: string | null) {
  if (!d) return "";
  return d.slice(0, 16).replace("T", " ");
}

async function viewAlert(a: any) {
  if (!a.is_read) {
    try {
      await markAlertRead(a.id);
      a.is_read = true;
    } catch (e) {}
  }
  uni.navigateTo({ url: `/pages/chat/detail?id=${a.session_id}` });
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.page-title { font-size: 20px; font-weight: bold; color: #303133; margin-bottom: 14px; display: block; }
.empty { text-align: center; color: #909399; padding: 40px 0; }
.card { background: #fff; padding: 14px 16px; border-radius: 10px; margin-bottom: 10px; position: relative; }
.card.unread { border-left: 3px solid #409eff; }
.header { display: flex; align-items: center; margin-bottom: 8px; }
.level-tag { font-size: 13px; font-weight: bold; }
.level-tag.red { color: #f56c6c; }
.level-tag.yellow { color: #e6a23c; }
.time { font-size: 12px; color: #909399; margin-left: 10px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #f56c6c; margin-left: auto; }
.summary-text { font-size: 14px; color: #606266; line-height: 1.5; margin-bottom: 6px; display: block; }
.action { font-size: 13px; color: #409eff; }
</style>