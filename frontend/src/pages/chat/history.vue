<template>
  <view class="container">
    <text class="page-title">对话记录</text>

    <view v-if="sessions.length === 0" class="empty">暂无对话记录</view>

    <view v-for="s in sessions" :key="s.id" class="card" @click="viewSession(s)">
      <view class="row">
        <text class="date">{{ formatDate(s.created_at) }}</text>
        <text class="risk-tag" :class="s.risk_level">
          {{ riskLabel(s.risk_level) }}
        </text>
      </view>
      <view class="summary" v-if="s.ai_summary">{{ s.ai_summary }}</view>
      <text class="arrow">查看详情 ›</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getMySessions, type ChatSession } from "@/api/chat";

const sessions = ref<ChatSession[]>([]);

onMounted(async () => {
  try {
    sessions.value = await getMySessions();
  } catch (e) {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
});

function formatDate(d: string | null) {
  if (!d) return "";
  return d.slice(0, 16).replace("T", " ");
}

function riskLabel(level: string) {
  const m: Record<string, string> = { none: "正常", yellow: "中度风险", red: "高危" };
  return m[level] || level;
}

function viewSession(s: ChatSession) {
  uni.navigateTo({ url: `/pages/chat/detail?id=${s.id}` });
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.page-title { font-size: 20px; font-weight: bold; color: #303133; margin-bottom: 14px; display: block; }
.empty { text-align: center; color: #909399; padding: 40px 0; }
.card { background: #fff; padding: 14px 16px; border-radius: 10px; margin-bottom: 10px; }
.row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.date { font-size: 13px; color: #909399; }
.risk-tag { font-size: 12px; padding: 2px 8px; border-radius: 4px; }
.risk-tag.none { color: #67c23a; background: #f0f9eb; }
.risk-tag.yellow { color: #e6a23c; background: #fdf6ec; }
.risk-tag.red { color: #f56c6c; background: #fef0f0; }
.summary { font-size: 13px; color: #606266; line-height: 1.5; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.arrow { font-size: 13px; color: #409eff; }
</style>