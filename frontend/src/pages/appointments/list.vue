<template>
  <view class="page">
    <view class="header">
      <text class="page-title">{{ isCounselor ? '来访者预约' : '我的预约' }}</text>
      <text v-if="appointments.length" class="page-count">{{ appointments.length }} 条</text>
    </view>

    <view v-if="appointments.length === 0" class="empty">
      <text class="empty-icon">📋</text>
      <text class="empty-text">暂无预约记录</text>
    </view>

    <view v-for="apt in appointments" :key="apt.id" class="card">
      <view class="card-hd">
        <text class="status-badge" :class="statusClass(apt.status)">
          {{ statusLabel(apt.status) }}
        </text>
        <text class="card-role-name">
          {{ isCounselor ? apt.visitor_name : apt.counselor_name }}
        </text>
      </view>

      <view class="card-body">
        <view class="info-row">
          <text class="info-icon">📅</text>
          <text class="info-val">{{ apt.date }}</text>
        </view>
        <view class="info-row">
          <text class="info-icon">⏰</text>
          <text class="info-val">{{ formatTime(apt.start_time) }} - {{ formatTime(apt.end_time) }}</text>
        </view>
        <view v-if="apt.notes" class="info-row">
          <text class="info-icon">💬</text>
          <text class="info-val notes-text">{{ apt.notes }}</text>
        </view>
        <view v-if="apt.confirmed_at" class="info-row">
          <text class="info-icon">✅</text>
          <text class="info-val">已确认: {{ apt.confirmed_at.slice(0, 10) }}</text>
        </view>
      </view>

      <view class="card-actions">
        <text
          v-if="apt.status === 'pending' && !isCounselor"
          class="action danger"
          @click="cancelApt(apt)"
        >取消预约</text>
        <text
          v-if="apt.status === 'pending' && isCounselor"
          class="action primary"
          @click="confirmApt(apt)"
        >确认预约</text>
        <text
          v-if="(apt.status === 'pending' || apt.status === 'confirmed') && isCounselor"
          class="action danger"
          @click="cancelApt(apt)"
        >取消</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useUserStore } from "@/store/user";
import { getMyAppointments, cancelAppointment, confirmAppointment } from "@/api/appointment";

const userStore = useUserStore();
const appointments = ref<any[]>([]);
const isCounselor = computed(() => userStore.userInfo?.role === "counselor");

onMounted(loadAppointments);

async function loadAppointments() {
  try {
    appointments.value = await getMyAppointments();
  } catch {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
}

function formatTime(t: string) {
  return t ? t.slice(0, 5) : "";
}

function statusLabel(s: string) {
  const m: Record<string, string> = {
    pending: "待确认", confirmed: "已确认", completed: "已完成", cancelled: "已取消",
  };
  return m[s] || s;
}

function statusClass(s: string) {
  return s === "confirmed" ? "confirmed"
    : s === "pending" ? "pending"
    : s === "cancelled" ? "cancelled"
    : "done";
}

async function cancelApt(apt: any) {
  const { confirm } = await uni.showModal({
    title: "取消预约",
    content: apt.date && apt.date === today
      ? "预约当天不可取消，如需调整请联系咨询师"
      : "确定取消此预约吗？",
  });
  if (!confirm) return;

  try {
    await cancelAppointment(apt.id);
    uni.showToast({ title: "已取消", icon: "success" });
    await loadAppointments();
  } catch (e: any) {
    uni.showToast({ title: e.detail || "取消失败", icon: "none" });
  }
}

const today = new Date().toISOString().slice(0, 10);

async function confirmApt(apt: any) {
  const { confirm } = await uni.showModal({
    title: "确认预约",
    content: "确认此预约后，来访者将收到通知。",
  });
  if (!confirm) return;
  try {
    await confirmAppointment(apt.id);
    uni.showToast({ title: "预约已确认", icon: "success", duration: 2000 });
    await loadAppointments();
  } catch (e: any) {
    uni.showToast({ title: e.detail || "操作失败", icon: "none" });
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

.header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: $text-primary;
}

.page-count {
  font-size: 13px;
  color: $text-muted;
}

.empty {
  text-align: center;
  padding: 60px 0;
}

.empty-icon {
  font-size: 40px;
  display: block;
  margin-bottom: 10px;
}

.empty-text {
  font-size: 14px;
  color: $text-muted;
}

.card {
  background: $card-bg;
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 10px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}

.card-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.status-badge {
  font-size: 12px;
  padding: 3px 12px;
  border-radius: 10px;
  font-weight: 500;
}
.status-badge.pending { color: #d4a56a; background: #faf3ef; }
.status-badge.confirmed { color: #5b8c7e; background: #e8f0ed; }
.status-badge.done { color: #67c23a; background: #f0f9eb; }
.status-badge.cancelled { color: $text-muted; background: #f5f5f5; }

.card-role-name {
  font-size: 13px;
  color: $text-secondary;
}

.card-body {
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 6px;
}

.info-icon {
  width: 20px;
  font-size: 14px;
  margin-right: 8px;
  text-align: center;
  flex-shrink: 0;
}

.info-val {
  font-size: 14px;
  color: $text-primary;
  line-height: 1.5;
}

.notes-text {
  color: $text-secondary;
  font-style: italic;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.action {
  font-size: 13px;
  font-weight: 500;
}

.action.primary { color: $primary; }
.action.danger { color: #c97b63; }
</style>
