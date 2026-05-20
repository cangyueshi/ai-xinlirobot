<template>
  <view class="page">
    <view class="page-header">
      <text class="page-title">预约咨询</text>
      <text class="counselor-name">咨询师: {{ counselorName }}</text>
    </view>

    <!-- 日期选择 -->
    <view class="section-card">
      <text class="section-label">选择日期</text>
      <picker mode="date" :value="selectedDate" :start="minDate" :end="maxDate" @change="onDateChange">
        <view class="picker-trigger">
          <text class="picker-text" :class="{ placeholder: !selectedDate }">
            {{ selectedDate || '点击选择日期' }}
          </text>
          <text class="picker-arrow">▼</text>
        </view>
      </picker>
    </view>

    <!-- 可选时间段 -->
    <view v-if="selectedDate">
      <view v-if="loading" class="status-text">加载中...</view>
      <view v-else-if="slots.length === 0" class="status-text">
        <text class="empty-icon">📅</text>
        <text class="empty-text">该日期暂无可用时间段</text>
      </view>

      <view v-else>
        <view class="section-card hint-card">
          <view class="hint-row">
            <view class="hint-dot primary"></view>
            <text class="hint-text">首选时间段（必选）</text>
          </view>
          <view class="hint-row">
            <view class="hint-dot backup"></view>
            <text class="hint-text">备选时间段（可选）</text>
          </view>
        </view>

        <text class="slot-title">可选时间段</text>
        <view
          v-for="slot in sortedSlots"
          :key="slot.id"
          class="slot-card"
          :class="{
            'is-primary': primarySlot?.id === slot.id,
            'is-backup': backupSlot?.id === slot.id,
          }"
          @click="selectSlot(slot)"
        >
          <view class="slot-left">
            <view class="slot-time">
              <text class="slot-hour">{{ formatTime(slot.start_time) }}</text>
              <text class="slot-sep">至</text>
              <text class="slot-hour">{{ formatTime(slot.end_time) }}</text>
            </view>
            <text class="slot-date">{{ slot.date }}</text>
          </view>
          <view class="slot-tags">
            <text v-if="primarySlot?.id === slot.id" class="tag tag-primary">首选</text>
            <text v-else-if="backupSlot?.id === slot.id" class="tag tag-backup">备选</text>
          </view>
        </view>

        <!-- 来访原因 — 通过 AI 对话收集 -->
        <view class="section-card">
          <text class="section-label">来访原因</text>
          <view v-if="collectedReason" class="reason-result">
            <text class="reason-result-text">{{ collectedReason }}</text>
            <text class="reason-result-link" @click="collectedReason = ''">重新收集</text>
          </view>
          <view v-else class="reason-prompt">
            <text class="reason-prompt-icon">💬</text>
            <view class="reason-prompt-text">
              <text>请通过 AI 对话告诉我们你的来访原因，以便咨询师提前了解你的情况。</text>
              <text class="reason-prompt-sub">你可以随时结束对话，AI 会自动总结你的来访原因。</text>
            </view>
          </view>
        </view>

        <view class="confirm-area">
          <text v-if="!primarySlot" class="confirm-hint">请先选择首选时间段</text>
          <button
            class="confirm-btn"
            :disabled="!primarySlot"
            @click="startAIChat"
          >{{ startChatLabel }}</button>
        </view>
      </view>
    </view>

    <view v-else class="date-hint">
      <text class="date-hint-icon">📅</text>
      <text class="date-hint-text">请先选择预约日期</text>
      <text class="date-hint-sub">可预约后天至未来一周内的时间</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { getCounselorAvailabilities, bookAppointment } from "@/api/appointment";

const counselorId = ref(0);
const counselorName = ref("");
const selectedDate = ref("");
const slots = ref<any[]>([]);
const primarySlot = ref<any>(null);
const backupSlot = ref<any>(null);
const loading = ref(false);

// 来访原因 — 通过 AI 对话收集
const collectedReason = ref("");

onLoad((options: any) => {
  counselorId.value = Number(options.counselorId);
  counselorName.value = options.name || "未知";
  // 从 AI 对话页面返回时携带已收集的来访原因
  if (options.reason) {
    collectedReason.value = options.reason;
  }
});

const startChatLabel = computed(() => {
  return collectedReason.value ? "下一步" : "开始AI对话收集来访原因";
});

function padDate(n: number) {
  return String(n).padStart(2, "0");
}

const today = new Date();
const minDate = `${today.getFullYear()}-${padDate(today.getMonth() + 1)}-${padDate(today.getDate() + 2)}`;
const maxDate = `${today.getFullYear()}-${padDate(today.getMonth() + 1)}-${padDate(today.getDate() + 7)}`;

function onDateChange(e: any) {
  selectedDate.value = e.detail.value;
  primarySlot.value = null;
  backupSlot.value = null;
  loadSlots();
}

async function loadSlots() {
  if (!selectedDate.value) return;
  loading.value = true;
  try {
    slots.value = await getCounselorAvailabilities(counselorId.value, selectedDate.value);
  } catch {
    uni.showToast({ title: "加载失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

const sortedSlots = computed(() => {
  return [...slots.value].sort((a, b) => {
    if (a.start_time < b.start_time) return -1;
    if (a.start_time > b.start_time) return 1;
    return 0;
  });
});

function formatTime(t: string) {
  return t ? t.slice(0, 5) : "";
}

function selectSlot(slot: any) {
  if (primarySlot.value?.id === slot.id) {
    primarySlot.value = null;
    return;
  }
  if (backupSlot.value?.id === slot.id) {
    backupSlot.value = null;
    return;
  }
  if (!primarySlot.value) {
    primarySlot.value = slot;
  } else if (!backupSlot.value && slot.id !== primarySlot.value.id) {
    backupSlot.value = slot;
  } else {
    primarySlot.value = slot;
    backupSlot.value = null;
  }
}

function startAIChat() {
  if (!primarySlot.value) return;

  if (collectedReason.value) {
    // 来访原因已收集，提交预约
    confirmBook();
    return;
  }

  // 去 AI 对话收集来访原因
  const params = {
    mode: "booking_reason",
    counselorId: String(counselorId.value),
    availabilityId: String(primarySlot.value.id),
    backupId: backupSlot.value ? String(backupSlot.value.id) : "",
    slotDate: primarySlot.value.date,
  };
  uni.navigateTo({ url: `/pages/chat/chat?${new URLSearchParams(params).toString()}` });
}

async function confirmBook() {
  if (!primarySlot.value) return;

  const primaryTime = `${formatTime(primarySlot.value.start_time)}-${formatTime(primarySlot.value.end_time)}`;
  let content = `预约时间: ${primaryTime}`;
  if (backupSlot.value) {
    const t = `${formatTime(backupSlot.value.start_time)}-${formatTime(backupSlot.value.end_time)}`;
    content += `\n备选: ${t}`;
  }
  if (collectedReason.value) {
    content += `\n来访原因: ${collectedReason.value}`;
  }

  const { confirm } = await uni.showModal({ title: "确认预约", content });
  if (!confirm) return;

  try {
    await bookAppointment({
      availability_id: primarySlot.value.id,
      backup_availability_id: backupSlot.value?.id || undefined,
      reason: collectedReason.value || undefined,
    });
    uni.showToast({ title: "预约已提交", icon: "success", duration: 2000 });
    setTimeout(() => uni.navigateBack(), 2000);
  } catch (e: any) {
    uni.showToast({ title: e.detail || "预约失败", icon: "none" });
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

.page-header {
  margin-bottom: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: $text-primary;
  display: block;
}

.counselor-name {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-top: 4px;
}

.section-card {
  background: $card-bg;
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 10px;
}

.picker-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: #fafafa;
  border-radius: 10px;
  border: 1px solid #e8e8e8;
}

.picker-text {
  font-size: 15px;
  color: $text-primary;
}

.picker-text.placeholder {
  color: $text-muted;
}

.picker-arrow {
  font-size: 10px;
  color: $text-muted;
}

.hint-card {
  padding: 12px 16px;
}

.hint-row {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
}

.hint-row:last-child { margin-bottom: 0; }

.hint-dot {
  width: 12px;
  height: 12px;
  border-radius: 4px;
  margin-right: 8px;
  flex-shrink: 0;
}

.hint-dot.primary { background: $primary; }
.hint-dot.backup { background: #d4a56a; }

.hint-text {
  font-size: 13px;
  color: $text-secondary;
}

.slot-title {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 8px;
  padding-left: 2px;
}

.slot-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: $card-bg;
  padding: 14px 16px;
  border-radius: 12px;
  margin-bottom: 8px;
  border: 2px solid transparent;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

.slot-card.is-primary {
  border-color: $primary;
  background: #f0f7f4;
}

.slot-card.is-backup {
  border-color: #d4a56a;
  background: #faf3ef;
}

.slot-left {
  flex: 1;
}

.slot-time {
  display: flex;
  align-items: center;
  gap: 8px;
}

.slot-hour {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
}

.slot-sep {
  font-size: 12px;
  color: $text-muted;
}

.slot-date {
  font-size: 12px;
  color: $text-secondary;
  display: block;
  margin-top: 2px;
}

.slot-tags {
  display: flex;
  gap: 6px;
}

.tag {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.tag-primary {
  color: #fff;
  background: $primary;
}

.tag-backup {
  color: #fff;
  background: #d4a56a;
}

// ====== 来访原因（AI 对话收集） ======
.reason-prompt {
  display: flex;
  gap: 10px;
  padding: 12px;
  background: #f0f7f4;
  border-radius: 12px;
  align-items: flex-start;
}

.reason-prompt-icon {
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 1px;
}

.reason-prompt-text {
  font-size: 13px;
  color: $text-secondary;
  line-height: 1.5;
}

.reason-prompt-sub {
  display: block;
  font-size: 12px;
  color: $text-muted;
  margin-top: 4px;
}

.reason-result {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: #f0f7f4;
  border-radius: 12px;
  border: 1px solid #d0e3dc;
}

.reason-result-text {
  flex: 1;
  font-size: 13px;
  color: $text-primary;
  line-height: 1.5;
}

.reason-result-link {
  font-size: 12px;
  color: $primary;
  flex-shrink: 0;
  margin-top: 2px;
}

.confirm-area {
  margin-top: 20px;
  text-align: center;
}

.confirm-hint {
  font-size: 13px;
  color: #c0822e;
  display: block;
  margin-bottom: 10px;
}

.confirm-btn {
  width: 80%;
  height: 48px;
  line-height: 48px;
  background: $primary;
  color: #fff;
  border-radius: 24px;
  font-size: 17px;
  font-weight: 600;
  border: none;
  box-shadow: 0 4px 12px rgba(91, 140, 126, 0.3);
}

.confirm-btn:active {
  transform: scale(0.97);
}

.confirm-btn[disabled] {
  background: #c0c4cc;
  box-shadow: none;
}

.status-text {
  text-align: center;
  color: $text-muted;
  padding: 40px 0;
  font-size: 14px;
}

.empty-icon {
  font-size: 36px;
  display: block;
  margin-bottom: 8px;
}

.empty-text {
  font-size: 14px;
  color: $text-muted;
}

.date-hint {
  text-align: center;
  padding: 80px 20px;
}

.date-hint-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.date-hint-text {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
  display: block;
}

.date-hint-sub {
  font-size: 13px;
  color: $text-muted;
  display: block;
  margin-top: 6px;
}
</style>
