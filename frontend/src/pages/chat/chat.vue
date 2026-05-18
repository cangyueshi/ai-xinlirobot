<template>
  <view class="container">
    <!-- 知情同意弹窗 -->
    <view v-if="showConsent" class="consent-overlay">
      <view class="consent-box">
        <text class="consent-title">知情同意说明</text>
        <view class="consent-body">
          <text>我是 AI 心理助手。在开始前请了解：</text>
          <text class="consent-item">1. 对话记录仅你和你选择的咨询师可见</text>
          <text class="consent-item">2. 我是AI助手，不能做诊断或开药</text>
          <text class="consent-item">3. 如检测到紧急危险，会通知咨询师</text>
          <text class="consent-item">4. 你随时可以结束对话</text>
        </view>
        <button class="btn-agree" @click="agreeConsent">了解并开始对话</button>
      </view>
    </view>

    <!-- 聊天区域 -->
    <scroll-view class="chat-area" scroll-y :scroll-top="scrollTop" ref="chatArea">
      <view v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
        <view class="bubble" :class="msg.role">
          <text>{{ msg.content }}</text>
        </view>
      </view>
      <view v-if="aiThinking" class="msg-row assistant">
        <view class="bubble assistant thinking">
          <text>正在思考...</text>
        </view>
      </view>
      <!-- 永久免责声明 -->
      <view class="disclaimer-row">
        <text>⚠ 本 AI 助手不能替代专业心理咨询诊断，紧急情况请拨打 120 或心理援助热线 400-161-9995</text>
      </view>
    </scroll-view>

    <!-- 输入区域 -->
    <view class="input-area">
      <input
        class="input-box"
        v-model="inputText"
        placeholder="输入你想说的话..."
        :disabled="sessionEnded"
        confirm-type="send"
        @confirm="sendMsg"
      />
      <button class="send-btn" @click="sendMsg" :disabled="!inputText || sessionEnded">发送</button>
      <button v-if="!sessionEnded && messages.length > 0" class="end-btn" @click="endChat">结束对话</button>
    </view>

    <!-- 对话结束提示 -->
    <view v-if="sessionEnded" class="ended-bar">
      <text>{{ endingMessage }}</text>
      <button class="back-btn" @click="goBack">返回首页</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, nextTick, onUnmounted } from "vue";
import { createSession, sendMessage, endSession } from "@/api/chat";

const showConsent = ref(true);
const sessionId = ref(0);
const messages = ref<{ role: string; content: string }[]>([]);
const inputText = ref("");
const aiThinking = ref(false);
const sessionEnded = ref(false);
const endingMessage = ref("");
const scrollTop = ref(0);

async function agreeConsent() {
  showConsent.value = false;
  try {
    const session = await createSession();
    sessionId.value = session.id;
    messages.value.push({
      role: "assistant",
      content: "你好，我是AI心理助手。今天想聊些什么呢？我会认真倾听。",
    });
  } catch (e) {
    uni.showToast({ title: "启动对话失败", icon: "none" });
  }
}

function scrollToBottom() {
  nextTick(() => {
    scrollTop.value = 99999;
  });
}

async function sendMsg() {
  const text = inputText.value.trim();
  if (!text || sessionEnded.value) return;
  inputText.value = "";
  messages.value.push({ role: "user", content: text });
  scrollToBottom();

  aiThinking.value = true;
  try {
    const reply = await sendMessage(sessionId.value, text);
    messages.value.push({ role: "assistant", content: reply.content });

    if (reply.crisis_alert) {
      const levelLabels: Record<string, string> = {
        level_1: "危机干预已启动，专业咨询师3分钟内将联系你",
        level_2: "危机干预已启动，专业咨询师10分钟内将联系你",
        level_3: "危机干预已启动，专业咨询师30分钟内将联系你",
      };
      messages.value.push({
        role: "system",
        content: levelLabels[reply.crisis_level || ""] || "危机预警已发送",
      });

      uni.showModal({
        title: "⚠️ 危机预警提醒",
        content: "本 AI 助手不能替代专业心理咨询诊断。我们已紧急通知专业咨询师，请保持联系。\n\n如果您处于紧急危险状态，请立即拨打 120 或心理援助热线 400-161-9995。",
        showCancel: false,
        confirmText: "我知道了",
      });
    }

    if (reply.crisis_cancelled) {
      messages.value.push({
        role: "system",
        content: "危机模式已解除，继续正常对话。",
      });
    }

    if (reply.session_ended) {
      sessionEnded.value = true;
      endingMessage.value = "对话已结束，AI 已生成分析报告供咨询师查看。";
    }
  } catch (e: any) {
    messages.value.push({
      role: "assistant",
      content: "抱歉，出现了一些问题，请稍后再试。",
    });
  } finally {
    aiThinking.value = false;
    scrollToBottom();
  }
}

async function endChat() {
  uni.showModal({
    title: "结束对话",
    content: "确定要结束本次对话吗？",
    success: async (res) => {
      if (!res.confirm) return;
      try {
        const result = await endSession(sessionId.value);
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
      } catch (e) {
        uni.showToast({ title: "结束失败", icon: "none" });
      }
    },
  });
}

function goBack() {
  uni.navigateBack();
}

onUnmounted(() => {
  if (!sessionEnded.value && sessionId.value) {
    endSession(sessionId.value).catch(() => {});
  }
});
</script>

<style lang="scss" scoped>
.container { display: flex; flex-direction: column; height: 100vh; background: #f0f2f5; }

.consent-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6); display: flex; align-items: center;
  justify-content: center; z-index: 100;
}
.consent-box {
  background: #fff; margin: 30px; border-radius: 12px; padding: 24px;
  width: calc(100% - 60px);
}
.consent-title { font-size: 20px; font-weight: bold; color: #303133; display: block; margin-bottom: 16px; }
.consent-body { margin-bottom: 20px; font-size: 14px; color: #606266; line-height: 1.8; }
.consent-item { display: block; margin-top: 6px; }
.btn-agree {
  width: 100%; height: 44px; line-height: 44px; background: #409eff;
  color: #fff; border-radius: 8px; font-size: 16px; border: none;
}

.chat-area { flex: 1; padding: 12px; overflow-y: auto; }
.msg-row { display: flex; margin-bottom: 14px; }
.msg-row.user { justify-content: flex-end; }
.msg-row.assistant { justify-content: flex-start; }
.msg-row.system { justify-content: center; }
.bubble {
  max-width: 75%; padding: 10px 14px; border-radius: 14px;
  font-size: 15px; line-height: 1.6; word-break: break-all;
}
.bubble.user { background: #409eff; color: #fff; border-bottom-right-radius: 4px; }
.bubble.assistant { background: #fff; color: #303133; border-bottom-left-radius: 4px; }
.bubble.system { background: #fdf6ec; color: #e6a23c; font-size: 13px; max-width: 85%; text-align: center; }
.bubble.thinking { color: #909399; font-style: italic; }
.disclaimer-row {
  text-align: center; padding: 8px 4px; margin-top: 4px;
}
.disclaimer-row text {
  font-size: 10px; color: #bbb; line-height: 1.4;
}

.input-area {
  display: flex; align-items: center; padding: 10px 12px;
  background: #fff; border-top: 1px solid #e4e7ed;
}
.input-box {
  flex: 1; height: 38px; padding: 0 12px; font-size: 15px;
  border: 1px solid #dcdfe6; border-radius: 20px; background: #f5f5f5;
}
.send-btn {
  margin-left: 8px; height: 38px; line-height: 38px; background: #409eff;
  color: #fff; border-radius: 20px; font-size: 14px; padding: 0 16px; border: none;
}
.end-btn {
  margin-left: 6px; height: 38px; line-height: 38px; background: #f56c6c;
  color: #fff; border-radius: 20px; font-size: 13px; padding: 0 12px; border: none;
}

.ended-bar {
  padding: 12px 16px; background: #fdf6ec; text-align: center; font-size: 13px; color: #e6a23c;
}
.back-btn {
  margin-top: 8px; height: 32px; line-height: 32px; background: #409eff;
  color: #fff; border-radius: 16px; font-size: 13px; padding: 0 20px; border: none;
}
</style>