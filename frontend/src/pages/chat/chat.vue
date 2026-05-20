<template>
  <view class="page">
    <!-- 顶部栏（含结束按钮） -->
    <view v-if="!showConsent && messages.length > 0" class="chat-header">
      <text class="chat-header-title">{{ bookingMode ? '收集来访原因' : 'AI 心理助手' }}</text>
      <text class="chat-header-end" @click="endChat">❌</text>
    </view>

    <!-- 知情同意弹窗 -->
    <view v-if="showConsent" class="consent-overlay">
      <view class="consent-dialog">
        <text class="consent-icon">🛡️</text>
        <text class="consent-title">知情同意</text>
        <view class="consent-items">
          <text class="consent-item">· 对话记录仅你和你选择的咨询师可见</text>
          <text class="consent-item">· 我是 AI 助手，不能做诊断或开药</text>
          <text class="consent-item">· 如检测到紧急危险，会通知咨询师</text>
          <text class="consent-item">· 你随时可以结束对话</text>
        </view>
        <button class="consent-btn" @click="agreeConsent">了解并开始对话</button>
      </view>
    </view>

    <!-- 聊天区域 -->
    <scroll-view
      class="chat-area"
      scroll-y
      :scroll-top="scrollTop"
      ref="chatArea"
    >
      <view class="chat-inner">
        <view
          v-for="(msg, i) in messages"
          :key="i"
          class="msg-row"
          :class="msg.role"
        >
          <!-- 头像 -->
          <view v-if="msg.role === 'assistant'" class="msg-avatar">
            <text class="msg-avatar-text">AI</text>
          </view>
          <view v-if="msg.role === 'user'" class="msg-avatar user-avatar-icon">
            <text class="msg-avatar-text">{{ myInitial }}</text>
          </view>

          <!-- 气泡 -->
          <view class="bubble-wrap">
            <view class="bubble" :class="msg.role">
              <text class="bubble-text">{{ msg.content }}</text>
            </view>
            <text class="bubble-time">{{ formatTime(msg.created_at) }}</text>
          </view>
        </view>

        <!-- AI 思考动画 -->
        <view v-if="aiThinking" class="msg-row assistant">
          <view class="msg-avatar">
            <text class="msg-avatar-text">AI</text>
          </view>
          <view class="bubble-wrap">
            <view class="bubble assistant thinking-bubble">
              <view class="thinking-dots">
                <view class="dot"></view>
                <view class="dot"></view>
                <view class="dot"></view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 永久免责声明 -->
      <view class="disclaimer">
        <text>⚠ AI 助手不能替代专业诊断，紧急情况请拨打 120 或心理援助热线 400-161-9995</text>
      </view>
    </scroll-view>

    <!-- 输入区域 -->
    <view v-if="!sessionEnded" class="input-area">
      <input
        class="input-box"
        v-model="inputText"
        placeholder="输入你想说的话..."
        :disabled="aiThinking"
        confirm-type="send"
        @confirm="sendMsg"
      />
      <button
        class="send-btn"
        :class="{ active: inputText }"
        :disabled="!inputText || aiThinking"
        @click="sendMsg"
      >发送</button>
    </view>

    <!-- 对话结束面板 -->
    <view v-if="sessionEnded" class="ended-panel">
      <view class="ended-header">
        <text class="ended-icon">💚</text>
        <text class="ended-title">{{ bookingMode ? '来访原因已收集' : '对话已结束' }}</text>
        <text class="ended-reason">{{ endingLabel }}</text>
      </view>
      <view v-if="bookingMode" class="booking-hint">
        <text class="booking-hint-text">点击「提交预约」完成预约，AI 会将会话摘要作为来访原因提交给咨询师。</text>
      </view>

      <!-- 评估摘要卡片 -->
      <view class="summary-card">
        <text class="summary-label">AI 评估摘要</text>
        <text class="summary-text">{{ assessmentSummary || endingMessage }}</text>
      </view>

      <view class="ended-actions">
        <button v-if="bookingMode" class="action-btn primary" @click="submitBooking">提交预约</button>
        <button v-else class="action-btn primary" @click="goBack">返回首页</button>
        <button class="action-btn outline" @click="restartChat">重新开始</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onUnmounted } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { createSession, sendMessage, endSession } from "@/api/chat";
import { bookAppointment } from "@/api/appointment";
import { useUserStore } from "@/store/user";

const userStore = useUserStore();
const showConsent = ref(true);
const sessionId = ref(0);
const messages = ref<{ role: string; content: string; created_at?: string }[]>([]);
const inputText = ref("");
const aiThinking = ref(false);
const sessionEnded = ref(false);
const endingMessage = ref("");
const assessmentSummary = ref("");
const scrollTop = ref(0);

// 预约模式
const bookingMode = ref(false);
const bookingCounselorId = ref(0);
const bookingAvailabilityId = ref(0);
const bookingBackupId = ref(0);

onLoad((options: any) => {
  if (options.mode === "booking_reason") {
    bookingMode.value = true;
    bookingCounselorId.value = Number(options.counselorId) || 0;
    bookingAvailabilityId.value = Number(options.availabilityId) || 0;
    bookingBackupId.value = Number(options.backupId) || 0;
  }
});

const myInitial = computed(() => {
  const name = userStore.userInfo?.display_name || "我";
  return name.charAt(0);
});

const endingLabel = computed(() => {
  const labels: Record<string, string> = {
    manual_end: "你主动结束了对话",
    free_limit_reached: "对话已达上限",
    info_complete: "信息已收集完整",
    user_wants_end: "你表达了结束意愿",
    meaningless_chat: "咨询范围之外",
    repeated_venting: "需要新信息",
  };
  return "— " + (labels[endingReason.value] || "对话已完成");
});

const endingReason = ref("manual_end");

async function agreeConsent() {
  showConsent.value = false;
  try {
    const session = await createSession();
    sessionId.value = session.id;
    const greeting = bookingMode.value
      ? "你好，我是 AI 心理助手。了解到你正在预约心理咨询，可以跟我说说你希望咨询师帮助你解决什么问题吗？不用担心，随便聊聊就好，我会帮你整理好来访原因。"
      : "你好，我是 AI 心理助手。今天想聊些什么呢？我会认真倾听。";
    messages.value.push({
      role: "assistant",
      content: greeting,
    });
  } catch {
    uni.showToast({ title: "启动对话失败", icon: "none" });
  }
}

async function sendMsg() {
  const text = inputText.value.trim();
  if (!text || sessionEnded.value || aiThinking.value) return;
  inputText.value = "";

  messages.value.push({ role: "user", content: text });
  scrollToBottom();

  aiThinking.value = true;
  try {
    const reply = await sendMessage(sessionId.value, text);
    messages.value.push({
      role: "assistant",
      content: reply.content,
      created_at: reply.created_at,
    });

    if (reply.crisis_alert) {
      const levelLabels: Record<string, string> = {
        level_1: "危机干预已启动，专业咨询师 3 分钟内将联系你",
        level_2: "危机干预已启动，专业咨询师 10 分钟内将联系你",
        level_3: "危机干预已启动，专业咨询师 30 分钟内将联系你",
      };
      messages.value.push({
        role: "system",
        content: levelLabels[reply.crisis_level || ""] || "危机预警已发送",
      });
    }

    if (reply.crisis_cancelled) {
      messages.value.push({
        role: "system",
        content: "危机模式已解除，继续正常对话。",
      });
    }

    if (reply.session_ended) {
      handleSessionEnd(reply, "manual_end");
    }
  } catch {
    messages.value.push({
      role: "assistant",
      content: "抱歉，出现了一些问题，请稍后再试。",
    });
  } finally {
    aiThinking.value = false;
    scrollToBottom();
  }
}

function handleSessionEnd(reply: any, reason: string) {
  sessionEnded.value = true;
  endingReason.value = reply.ending_reason || reason;
  endingMessage.value = reply.content || "感谢你的信任，对话已结束。";

  // 提取评估摘要（去掉模板格式，提取核心内容）
  const content = reply.content || "";
  // 尝试从 Ending Template 中提取 assessment 部分
  const match = content.match(/我初步判断你目前正经历：\n([\s\S]*?)(?:\n\n|\n1[.、])/);
  if (match) {
    assessmentSummary.value = match[1].trim();
  } else {
    assessmentSummary.value = content;
  }
}

async function endChat() {
  const { confirm } = await uni.showModal({
    title: "结束对话",
    content: "确定要结束本次对话吗？AI 将生成评估报告。",
  });
  if (!confirm) return;

  aiThinking.value = true;
  try {
    const result = await endSession(sessionId.value);
    const aiMsg = result.ai_summary || "感谢你的信任，对话已结束。";
    messages.value.push({
      role: "assistant",
      content: aiMsg,
    });
    assessmentSummary.value = aiMsg;
    sessionEnded.value = true;

    const riskLabels: Record<string, string> = {
      none: "未检测到风险",
      yellow: "检测到中度风险信号，已通知咨询师",
      red: "检测到高危信号，已紧急通知咨询师",
    };
    messages.value.push({
      role: "system",
      content: riskLabels[result.risk_level] || "对话已结束",
    });
    scrollToBottom();
  } catch {
    uni.showToast({ title: "结束失败", icon: "none" });
  } finally {
    aiThinking.value = false;
  }
}

function scrollToBottom() {
  nextTick(() => {
    scrollTop.value = 99999;
  });
}

async function submitBooking() {
  if (!bookingAvailabilityId.value) {
    uni.showToast({ title: "预约信息缺失", icon: "none" });
    return;
  }
  try {
    await bookAppointment({
      availability_id: bookingAvailabilityId.value,
      backup_availability_id: bookingBackupId.value || undefined,
      reason: assessmentSummary.value || endingMessage.value,
    });
    uni.showToast({ title: "预约已提交", icon: "success", duration: 2000 });
    setTimeout(() => uni.navigateBack(), 2000);
  } catch (e: any) {
    uni.showToast({ title: e.detail || "预约失败", icon: "none" });
  }
}

function goBack() {
  uni.navigateBack();
}

function restartChat() {
  sessionEnded.value = false;
  sessionId.value = 0;
  messages.value = [];
  inputText.value = "";
  endingMessage.value = "";
  assessmentSummary.value = "";
  endingReason.value = "manual_end";
  agreeConsent();
}

function formatTime(t?: string) {
  if (!t) return "";
  const d = new Date(t);
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

onUnmounted(() => {
  if (!sessionEnded.value && sessionId.value) {
    endSession(sessionId.value).catch(() => {});
  }
});
</script>

<style lang="scss" scoped>
// ====== 色彩 ======
$primary: #5b8c7e;
$primary-light: #e8f0ed;
$bg: #f5f3ef;
$bubble-user: #5b8c7e;
$bubble-assistant: #ffffff;
$text-primary: #2c3e50;
$text-secondary: #7a8a8a;
$text-muted: #aab7b7;

.page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: $bg;
  position: relative;
}

// ====== 知情同意弹窗 ======
.consent-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(44, 62, 80, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.consent-dialog {
  width: calc(100% - 48px);
  max-width: 320px;
  background: #fff;
  border-radius: 24px;
  padding: 32px 24px 24px;
  text-align: center;
}

.consent-icon {
  font-size: 36px;
  margin-bottom: 12px;
  display: block;
}

.consent-title {
  font-size: 20px;
  font-weight: 700;
  color: $text-primary;
  display: block;
  margin-bottom: 16px;
}

.consent-items {
  text-align: left;
  margin-bottom: 24px;
}

.consent-item {
  display: block;
  font-size: 13px;
  color: $text-secondary;
  line-height: 1.8;
  padding-left: 4px;
}

.consent-btn {
  width: 100%;
  height: 46px;
  line-height: 46px;
  background: $primary;
  color: #fff;
  border-radius: 23px;
  font-size: 15px;
  font-weight: 600;
  border: none;
}

.consent-btn:active {
  opacity: 0.85;
}

// ====== 聊天区域 ======
.chat-area {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.chat-inner {
  padding: 16px 16px 8px;
}

.msg-row {
  display: flex;
  margin-bottom: 18px;
  align-items: flex-start;
}

.msg-row.user {
  flex-direction: row-reverse;
}

.msg-row.system {
  justify-content: center;
}

.msg-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 700;
}

.msg-row.assistant .msg-avatar {
  background: $primary-light;
  color: $primary;
  margin-right: 10px;
}

.user-avatar-icon {
  background: #dce8e4;
  color: $primary;
  margin-left: 10px;
}

.bubble-wrap {
  max-width: 72%;
  display: flex;
  flex-direction: column;
}

.msg-row.user .bubble-wrap {
  align-items: flex-end;
}

.bubble {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.6;
  word-break: break-word;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.bubble.assistant {
  background: $bubble-assistant;
  color: $text-primary;
  border-bottom-left-radius: 4px;
}

.bubble.user {
  background: $bubble-user;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.bubble-text {
  white-space: pre-wrap;
}

.bubble-time {
  font-size: 11px;
  color: $text-muted;
  margin-top: 4px;
  padding: 0 4px;
}

.msg-row.system .bubble {
  background: #fdf6ec;
  color: #c0822e;
  font-size: 13px;
  text-align: center;
  max-width: 85%;
  border-radius: 12px;
  padding: 10px 14px;
}

// ====== 思考动画 ======
.thinking-bubble {
  padding: 14px 18px;
}

.thinking-dots {
  display: flex;
  align-items: center;
  gap: 5px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: $text-muted;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
.dot:nth-child(3) { animation-delay: 0s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

// ====== 免责 ======
.disclaimer {
  padding: 10px 16px 16px;
  text-align: center;
}

.disclaimer text {
  font-size: 10px;
  color: #c0c4cc;
  line-height: 1.5;
}

// ====== 顶部栏 ======
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  flex-shrink: 0;
}

.chat-header-title {
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
}

.chat-header-end {
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
}

// ====== 输入区域 ======
.input-area {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  padding-bottom: calc(10px + env(safe-area-inset-bottom, 0px));
  background: #fff;
  border-top: 1px solid #e8e8e8;
}

.input-box {
  flex: 1;
  max-height: 150px;
  min-height: 40px;
  padding: 10px 14px;
  font-size: 15px;
  border: none;
  border-radius: 20px;
  background: #f0f0f0;
  outline: none;
  overflow-y: auto;
  line-height: 1.4;
  resize: none;
}

.send-btn {
  margin-left: 8px;
  height: 38px;
  line-height: 38px;
  border-radius: 19px;
  font-size: 14px;
  padding: 0 18px;
  border: none;
  background: #d0d5d5;
  color: #fff;
  transition: all 0.2s;
}

.send-btn.active {
  background: $primary;
}

.send-btn:active {
  transform: scale(0.95);
}

.send-btn[disabled] {
  opacity: 0.6;
}

// ====== 结束面板 ======
.ended-panel {
  padding: 20px 16px calc(20px + env(safe-area-inset-bottom, 0px));
  background: #fff;
  border-top: 1px solid #e8e8e8;
}

.ended-header {
  text-align: center;
  margin-bottom: 16px;
}

.ended-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
}

.ended-title {
  font-size: 18px;
  font-weight: 700;
  color: $text-primary;
  display: block;
}

.ended-reason {
  font-size: 12px;
  color: $text-muted;
  display: block;
  margin-top: 4px;
}

.summary-card {
  background: $primary-light;
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 16px;
}

.booking-hint {
  margin-bottom: 16px;
  padding: 10px 14px;
  background: #fdf6ec;
  border-radius: 10px;
}

.booking-hint-text {
  font-size: 12px;
  color: #c0822e;
  line-height: 1.5;
  display: block;
}

.summary-label {
  font-size: 12px;
  font-weight: 600;
  color: $primary;
  display: block;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.summary-text {
  font-size: 14px;
  color: $text-primary;
  line-height: 1.7;
  display: block;
  white-space: pre-wrap;
}

.ended-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  height: 44px;
  line-height: 44px;
  border-radius: 22px;
  font-size: 15px;
  font-weight: 600;
  text-align: center;
  border: none;
}

.action-btn.primary {
  background: $primary;
  color: #fff;
}

.action-btn.primary:active {
  opacity: 0.85;
}

.action-btn.outline {
  background: #fff;
  color: $primary;
  border: 1.5px solid $primary;
}

.action-btn.outline:active {
  background: $primary-light;
}
</style>
