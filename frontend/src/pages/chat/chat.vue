<template>
  <view class="page">
    <!-- 顶部栏 -->
    <view v-if="!showConsent && messages.length > 0" class="chat-header">
      <text class="chat-header-title">{{ bookingMode ? '来访原因' : 'AI 心理助手' }}</text>
      <view class="chat-header-end" @click="endChat">
        <text class="end-icon">&times;</text>
      </view>
    </view>

    <!-- 知情同意 -->
    <view v-if="showConsent" class="consent-overlay">
      <view class="consent-dialog">
        <view class="consent-top">
          <view class="consent-icon-wrap">
            <text class="consent-icon-symbol">&#x2763;</text>
          </view>
        </view>
        <text class="consent-title">开始对话前</text>
        <view class="consent-items">
          <view class="consent-item">
            <text class="consent-dot">&bull;</text>
            <text class="consent-text">对话记录仅你和咨询师可见</text>
          </view>
          <view class="consent-item">
            <text class="consent-dot">&bull;</text>
            <text class="consent-text">AI 不能做诊断或开药</text>
          </view>
          <view class="consent-item">
            <text class="consent-dot">&bull;</text>
            <text class="consent-text">检测到紧急情况会通知咨询师</text>
          </view>
          <view class="consent-item">
            <text class="consent-dot">&bull;</text>
            <text class="consent-text">你随时可以结束对话</text>
          </view>
        </view>
        <button class="consent-btn" @click="agreeConsent">了解，开始对话</button>
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
          <view v-if="msg.role === 'assistant'" class="msg-avatar">
            <text class="msg-avatar-text">AI</text>
          </view>

          <view class="bubble-wrap">
            <view class="bubble" :class="msg.role">
              <text class="bubble-text">{{ msg.content }}</text>
            </view>
            <text class="bubble-time">{{ formatTime(msg.created_at) }}</text>
          </view>

          <view v-if="msg.role === 'user'" class="msg-avatar user-av">
            <text class="msg-avatar-text">{{ myInitial }}</text>
          </view>
        </view>

        <!-- 系统消息 -->
        <view v-for="(msg, i) in messages.filter(m => m.role === 'system')" :key="'sys-' + i" class="msg-row system">
          <view class="sys-bubble">{{ msg.content }}</view>
        </view>

        <!-- AI 思考中 -->
        <view v-if="aiThinking" class="msg-row assistant">
          <view class="msg-avatar">
            <text class="msg-avatar-text">AI</text>
          </view>
          <view class="bubble-wrap">
            <view class="bubble assistant think-bubble">
              <view class="think-dots">
                <view class="tdot"></view>
                <view class="tdot"></view>
                <view class="tdot"></view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <view class="disclaimer">
        <text>AI 不能替代专业诊断，紧急情况请拨打 120 或心理援助热线 400-161-9995</text>
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
        :class="{ 'send-btn-active': inputText }"
        :disabled="!inputText || aiThinking"
        @click="sendMsg"
      >
        <text class="send-arrow">&rarr;</text>
      </button>
    </view>

    <!-- 结束面板 -->
    <view v-if="sessionEnded" class="ended-panel">
      <view class="ended-header">
        <view class="ended-icon-wrap">
          <text class="ended-icon-symbol">&#x2764;</text>
        </view>
        <text class="ended-title">{{ bookingMode ? '来访原因已收集' : '对话已结束' }}</text>
        <text class="ended-reason">{{ endingLabel }}</text>
      </view>

      <view v-if="bookingMode" class="booking-hint">
        <text class="booking-hint-text">点击「提交预约」完成预约，AI 会将会话摘要作为来访原因提交给咨询师。</text>
      </view>

      <view class="summary-card">
        <text class="summary-caption">AI 评估摘要</text>
        <text class="summary-main">{{ assessmentSummary || endingMessage }}</text>
      </view>

      <view class="ended-actions">
        <button v-if="bookingMode" class="act-btn act-primary" @click="submitBooking">提交预约</button>
        <button v-else class="act-btn act-primary" @click="goBack">返回首页</button>
        <button class="act-btn act-outline" @click="restartChat">重新开始</button>
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
      ? "你好，我是 AI 心理助手。了解到你正在预约心理咨询，可以跟我说说你希望咨询师帮你解决什么问题吗？不用担心，随便聊聊就好，我会帮你整理好来访原因。"
      : "你好，我是 AI 心理助手。今天想聊些什么呢？我会认真倾听。";
    messages.value.push({ role: "assistant", content: greeting });
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
      messages.value.push({ role: "system", content: "危机模式已解除" });
    }
    if (reply.session_ended) {
      handleSessionEnd(reply, "manual_end");
    }
  } catch {
    messages.value.push({ role: "assistant", content: "抱歉，出现了一些问题，请稍后再试。" });
  } finally {
    aiThinking.value = false;
    scrollToBottom();
  }
}

function handleSessionEnd(reply: any, reason: string) {
  sessionEnded.value = true;
  endingReason.value = reply.ending_reason || reason;
  endingMessage.value = reply.content || "感谢你的信任，对话已结束。";
  const content = reply.content || "";
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
    messages.value.push({ role: "assistant", content: aiMsg });
    assessmentSummary.value = aiMsg;
    sessionEnded.value = true;
    const riskLabels: Record<string, string> = {
      none: "未检测到风险",
      yellow: "检测到中度风险信号，已通知咨询师",
      red: "检测到高危信号，已紧急通知咨询师",
    };
    messages.value.push({ role: "system", content: riskLabels[result.risk_level] || "对话已结束" });
    scrollToBottom();
  } catch {
    uni.showToast({ title: "结束失败", icon: "none" });
  } finally {
    aiThinking.value = false;
  }
}

function scrollToBottom() {
  nextTick(() => { scrollTop.value = 99999; });
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

function goBack() { uni.navigateBack(); }

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
// ====================================================
//  Warm Amber Chat - 温暖琥珀聊天配色
// ====================================================
$bg-main:       #FDF8F4;
$bg-card:       #FFFFFF;
$primary:       #D4956A;
$primary-dark:  #B87A52;
$primary-light: #F0DCC8;
$primary-pale:  #F8EDE2;

$text-primary:  #3D322A;
$text-secondary:#8A8275;
$text-muted:    #B5A99A;

$bubble-ai:     $bg-card;
$bubble-user:   $primary;

$border-soft:   #E8E0D0;
$shadow-soft:   0 2px 8px rgba(61, 50, 42, 0.05);
$shadow-bubble: 0 1px 4px rgba(61, 50, 42, 0.06);

$radius:        20px;
$radius-pill:   30px;
$font-stack:    -apple-system, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;

.page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: $bg-main;
  position: relative;
  font-family: $font-stack;
}

// ====================================================
//  顶部栏
// ====================================================
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: $bg-card;
  border-bottom: 1px solid $border-soft;
  flex-shrink: 0;
}

.chat-header-title {
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
  letter-spacing: 0.02em;
}

.chat-header-end {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: $bg-main;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.end-icon {
  font-size: 18px;
  color: $text-muted;
  font-weight: 300;
  line-height: 1;
}

.chat-header-end:active {
  background: $border-soft;
}

// ====================================================
//  知情同意
// ====================================================
.consent-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(61, 50, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.consent-dialog {
  width: calc(100% - 56px);
  max-width: 320px;
  background: $bg-card;
  border-radius: 28px;
  padding: 36px 28px 28px;
  text-align: center;
  animation: fadeUp 0.35s ease;
}

.consent-top {
  margin-bottom: 16px;
}

.consent-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: $primary-pale;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.consent-icon-symbol {
  font-size: 24px;
  color: $primary;
}

.consent-title {
  font-size: 19px;
  font-weight: 700;
  color: $text-primary;
  display: block;
  margin-bottom: 20px;
  letter-spacing: 0.02em;
}

.consent-items {
  text-align: left;
  margin-bottom: 24px;
}

.consent-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
  gap: 8px;
}

.consent-dot {
  font-size: 14px;
  color: $primary;
  line-height: 1.6;
  flex-shrink: 0;
}

.consent-text {
  font-size: 13px;
  color: $text-secondary;
  line-height: 1.6;
}

.consent-btn {
  width: 100%;
  height: 48px;
  line-height: 48px;
  background: $primary;
  color: #fff;
  border-radius: $radius-pill;
  font-size: 15px;
  font-weight: 600;
  border: none;
  letter-spacing: 0.03em;
}

.consent-btn:active {
  opacity: 0.85;
}

// ====================================================
//  聊天区域
// ====================================================
.chat-area {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.chat-inner {
  padding: 20px 16px 8px;
}

.msg-row {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}

.msg-row.user {
  flex-direction: row-reverse;
}

.msg-row.system {
  justify-content: center;
}

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 700;
}

.msg-row.assistant .msg-avatar {
  background: $primary-light;
  color: $primary-dark;
  margin-right: 10px;
}

.user-av {
  background: $primary-light;
  color: $primary-dark;
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
  padding: 12px 18px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.65;
  word-break: break-word;
}

.bubble.assistant {
  background: $bubble-ai;
  color: $text-primary;
  border-bottom-left-radius: 4px;
  box-shadow: $shadow-bubble;
}

.bubble.user {
  background: $bubble-user;
  color: #fff;
  border-bottom-right-radius: 4px;
  box-shadow: $shadow-bubble;
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

//  系统消息
.sys-bubble {
  background: #FBF5E8;
  color: #A0853A;
  font-size: 12px;
  text-align: center;
  max-width: 80%;
  border-radius: 12px;
  padding: 8px 14px;
  line-height: 1.5;
}

//  思考动画
.think-bubble {
  padding: 14px 18px;
}

.think-dots {
  display: flex;
  align-items: center;
  gap: 5px;
}

.tdot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: $text-muted;
  animation: bounce 1.4s infinite ease-in-out both;
}

.tdot:nth-child(1) { animation-delay: -0.32s; }
.tdot:nth-child(2) { animation-delay: -0.16s; }
.tdot:nth-child(3) { animation-delay: 0s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

//  免责
.disclaimer {
  padding: 8px 16px 16px;
  text-align: center;
}

.disclaimer text {
  font-size: 10px;
  color: $text-muted;
  line-height: 1.5;
}

// ====================================================
//  输入区域
// ====================================================
.input-area {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  padding-bottom: calc(10px + env(safe-area-inset-bottom, 0px));
  background: $bg-card;
  border-top: 1px solid $border-soft;
}

.input-box {
  flex: 1;
  max-height: 150px;
  min-height: 42px;
  padding: 11px 16px;
  font-size: 15px;
  border: none;
  border-radius: $radius-pill;
  background: $bg-main;
  outline: none;
  overflow-y: auto;
  line-height: 1.4;
  resize: none;
  color: $text-primary;
}

.input-box::placeholder {
  color: $text-muted;
}

.send-btn {
  margin-left: 8px;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: none;
  background: $border-soft;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s ease;
  flex-shrink: 0;
  padding: 0;
  line-height: 1;
}

.send-btn-active {
  background: $primary;
  box-shadow: 0 2px 8px rgba($primary, 0.3);
}

.send-btn:active:not([disabled]) {
  transform: scale(0.9);
}

.send-btn[disabled] {
  opacity: 0.5;
}

.send-arrow {
  font-size: 18px;
  font-weight: 400;
  line-height: 1;
}

// ====================================================
//  结束面板
// ====================================================
.ended-panel {
  padding: 24px 20px;
  padding-bottom: calc(24px + env(safe-area-inset-bottom, 0px));
  background: $bg-card;
  border-top: 1px solid $border-soft;
}

.ended-header {
  text-align: center;
  margin-bottom: 20px;
}

.ended-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: $primary-pale;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
}

.ended-icon-symbol {
  font-size: 22px;
  color: $primary;
}

.ended-title {
  font-size: 18px;
  font-weight: 700;
  color: $text-primary;
  display: block;
  letter-spacing: 0.02em;
}

.ended-reason {
  font-size: 12px;
  color: $text-muted;
  display: block;
  margin-top: 4px;
}

.booking-hint {
  margin-bottom: 16px;
  padding: 10px 14px;
  background: #FBF5E8;
  border-radius: 12px;
}

.booking-hint-text {
  font-size: 12px;
  color: #A0853A;
  line-height: 1.5;
  display: block;
}

.summary-card {
  background: $primary-pale;
  border-radius: $radius;
  padding: 18px;
  margin-bottom: 20px;
}

.summary-caption {
  font-size: 11px;
  font-weight: 600;
  color: $primary;
  display: block;
  margin-bottom: 8px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.summary-main {
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

.act-btn {
  flex: 1;
  height: 46px;
  line-height: 46px;
  border-radius: $radius-pill;
  font-size: 15px;
  font-weight: 600;
  text-align: center;
  border: none;
  letter-spacing: 0.02em;
}

.act-primary {
  background: $primary;
  color: #fff;
}

.act-primary:active {
  opacity: 0.85;
}

.act-outline {
  background: #fff;
  color: $primary;
  border: 1.5px solid $primary;
}

.act-outline:active {
  background: $primary-pale;
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
