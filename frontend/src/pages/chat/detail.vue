<template>
  <view class="container">
    <view v-if="sessionInfo" class="info-bar">
      <text class="risk-tag" :class="sessionInfo.risk_level">
        {{ riskLabel(sessionInfo.risk_level) }}
      </text>
      <text class="date">{{ formatDate(sessionInfo.created_at) }}</text>
    </view>

    <view class="chat-area">
      <view v-for="msg in messages" :key="msg.id" class="msg-row" :class="msg.role">
        <view class="bubble" :class="msg.role">
          <text>{{ msg.content }}</text>
        </view>
      </view>
    </view>

    <view v-if="sessionInfo?.ai_summary" class="summary-box">
      <text class="summary-title">AI 分析摘要</text>
      <text class="summary-text">{{ sessionInfo.ai_summary }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getSessionMessages, getMySessions } from "@/api/chat";

const sessionId = ref(0);
const sessionInfo = ref<any>(null);
const messages = ref<any[]>([]);

onMounted(async () => {
  const pages = getCurrentPages();
  sessionId.value = Number((pages[pages.length - 1].options as any).id);
  try {
    const sessions = await getMySessions();
    sessionInfo.value = sessions.find((s: any) => s.id === sessionId.value);
    messages.value = await getSessionMessages(sessionId.value);
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
</script>

<style lang="scss" scoped>
.container { display: flex; flex-direction: column; height: 100vh; background: #f0f2f5; }
.info-bar { padding: 10px 16px; background: #fff; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; }
.risk-tag { font-size: 13px; padding: 2px 10px; border-radius: 4px; }
.risk-tag.none { color: #67c23a; background: #f0f9eb; }
.risk-tag.yellow { color: #e6a23c; background: #fdf6ec; }
.risk-tag.red { color: #f56c6c; background: #fef0f0; }
.date { font-size: 13px; color: #909399; }
.chat-area { flex: 1; padding: 12px; overflow-y: auto; }
.msg-row { display: flex; margin-bottom: 12px; }
.msg-row.user { justify-content: flex-end; }
.msg-row.assistant { justify-content: flex-start; }
.bubble { max-width: 75%; padding: 10px 14px; border-radius: 14px; font-size: 14px; line-height: 1.6; }
.bubble.user { background: #409eff; color: #fff; }
.bubble.assistant { background: #fff; color: #303133; }
.summary-box { background: #f0f9eb; padding: 16px; margin: 0 12px 12px; border-radius: 10px; }
.summary-title { font-size: 14px; font-weight: bold; color: #67c23a; display: block; margin-bottom: 6px; }
.summary-text { font-size: 13px; color: #606266; line-height: 1.6; }
</style>