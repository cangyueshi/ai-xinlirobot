<template>
  <view class="page">
    <!-- 对话信息栏 -->
    <view class="info-bar">
      <view class="info-left">
        <text class="info-risk" :class="sessionInfo?.risk_level">
          {{ riskLabel(sessionInfo?.risk_level) }}
        </text>
        <text class="info-date">{{ formatDate(sessionInfo?.created_at) }}</text>
      </view>
      <view v-if="visitorId" class="info-right">
        <text class="info-visitor">来访者: {{ visitorName || 'ID ' + visitorId }}</text>
      </view>
    </view>

    <!-- 消息区域 -->
    <scroll-view class="chat-area" scroll-y>
      <view v-for="msg in messages" :key="msg.id" class="msg-row" :class="msg.role">
        <view v-if="msg.role === 'assistant'" class="msg-avatar">AI</view>
        <view class="bubble-wrap">
          <view class="bubble" :class="msg.role">
            <text>{{ msg.content }}</text>
          </view>
          <text class="msg-time">{{ formatTime(msg.created_at) }}</text>
        </view>
        <view v-if="msg.role === 'user'" class="msg-avatar user-ava">{{ myInitial }}</view>
      </view>
    </scroll-view>

    <!-- AI 分析摘要（咨询师版，含指导建议） -->
    <view v-if="counselorSummary || sessionInfo?.ai_summary" class="summary-box">
      <view class="summary-header">
        <text class="summary-icon">📋</text>
        <text class="summary-title">AI 分析摘要（咨询师版）</text>
      </view>
      <text class="summary-text">{{ counselorSummary || sessionInfo?.ai_summary }}</text>
      <view v-if="sessionInfo?.ai_summary" class="summary-visitor-version" @click="showVisitorVersion = !showVisitorVersion">
        <text class="summary-toggle">{{ showVisitorVersion ? '收起' : '查看来访者版本' }}</text>
      </view>
      <text v-if="showVisitorVersion && sessionInfo?.ai_summary" class="summary-text visitor-version">
        {{ sessionInfo.ai_summary }}
      </text>
      <view class="summary-footer">
        <text class="summary-risk" v-if="sessionInfo?.risk_summary">
          风险: {{ sessionInfo.risk_summary }}
        </text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { getSessionMessages, getMySessions } from "@/api/chat";

const sessionId = ref(0);
const visitorId = ref("");
const visitorName = ref("");
const sessionInfo = ref<any>(null);
const messages = ref<any[]>([]);

const showVisitorVersion = ref(false);

const counselorSummary = computed(() => {
  return (sessionInfo.value as any)?.counselor_summary || "";
});

const myInitial = computed(() => {
  if (visitorName.value) return visitorName.value.charAt(0);
  return "?";
});

onMounted(async () => {
  const pages = getCurrentPages();
  const opts = (pages[pages.length - 1].options as any);
  sessionId.value = Number(opts.id);
  visitorId.value = opts.visitorId || "";
  visitorName.value = opts.visitorName ? decodeURIComponent(opts.visitorName) : "";

  try {
    const sessions = await getMySessions();
    sessionInfo.value = sessions.find((s: any) => s.id === sessionId.value);
    messages.value = await getSessionMessages(sessionId.value);
  } catch {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
});

function formatDate(d: string | null) {
  if (!d) return "";
  return d.slice(0, 16).replace("T", " ");
}

function formatTime(t: string | null) {
  if (!t) return "";
  const d = new Date(t);
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

function riskLabel(level: string) {
  const m: Record<string, string> = { none: "正常", yellow: "中度", red: "高危" };
  return m[level] || level;
}
</script>

<style lang="scss" scoped>
$bg: #f5f3ef;
$primary: #5b8c7e;
$text-primary: #2c3e50;
$text-secondary: #7a8a8a;
$text-muted: #aab7b7;

.page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: $bg;
}

.info-bar {
  padding: 12px 16px;
  background: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  flex-wrap: wrap;
  gap: 6px;
}

.info-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-risk {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 4px;
  font-weight: 500;
}
.info-risk.none { color: #67c23a; background: #f0f9eb; }
.info-risk.yellow { color: #e6a23c; background: #fdf6ec; }
.info-risk.red { color: #f56c6c; background: #fef0f0; }

.info-date {
  font-size: 12px;
  color: $text-muted;
}

.info-visitor {
  font-size: 12px;
  color: $text-secondary;
  background: #f5f5f5;
  padding: 3px 10px;
  border-radius: 10px;
}

.chat-area {
  flex: 1;
  padding: 12px 16px;
  overflow-y: auto;
}

.msg-row {
  display: flex;
  margin-bottom: 16px;
  align-items: flex-start;
}

.msg-row.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 700;
  margin: 0 8px;
  background: #e8f0ed;
  color: $primary;
}

.user-ava {
  background: #dce8e4;
}

.bubble-wrap {
  max-width: 72%;
}

.bubble {
  padding: 10px 14px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.bubble.assistant {
  background: #fff;
  color: $text-primary;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.bubble.user {
  background: $primary;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.msg-time {
  font-size: 10px;
  color: $text-muted;
  margin-top: 3px;
  display: block;
  padding: 0 2px;
}

.summary-box {
  margin: 0 12px 12px;
  background: #f0f9eb;
  border-radius: 14px;
  padding: 16px;
}

.summary-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.summary-icon {
  font-size: 16px;
}

.summary-title {
  font-size: 14px;
  font-weight: 600;
  color: #67c23a;
}

.summary-text {
  font-size: 13px;
  color: $text-secondary;
  line-height: 1.7;
  display: block;
}

.summary-footer {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid rgba(0,0,0,0.05);
}

.summary-risk {
  font-size: 12px;
  color: #e6a23c;
}

.summary-visitor-version {
  margin-top: 8px;
}

.summary-toggle {
  font-size: 12px;
  color: $primary;
}

.visitor-version {
  margin-top: 8px;
  padding: 10px;
  background: rgba(255,255,255,0.5);
  border-radius: 8px;
  font-size: 12px;
}
</style>
