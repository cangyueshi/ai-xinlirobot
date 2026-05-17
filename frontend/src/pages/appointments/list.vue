<template>
  <view class="container">
    <text class="page-title">
      {{ isCounselor ? "来访者预约" : "我的预约" }}
    </text>

    <view v-if="appointments.length === 0" class="empty">暂无预约记录</view>

    <view v-for="apt in appointments" :key="apt.id" class="card">
      <view class="card-header">
        <text class="status-tag" :class="statusClass(apt.status)">
          {{ statusLabel(apt.status) }}
        </text>
        <text v-if="isCounselor && apt.visitor_name" class="visitor-name">
          来访者：{{ apt.visitor_name }}
        </text>
        <text v-if="!isCounselor && apt.counselor_name" class="counselor-name">
          咨询师：{{ apt.counselor_name }}
        </text>
      </view>

      <view class="row">
        <text class="label">日期</text>
        <text class="value">{{ apt.date }}</text>
      </view>
      <view class="row">
        <text class="label">时间</text>
        <text class="value">{{ formatTime(apt.start_time) }} - {{ formatTime(apt.end_time) }}</text>
      </view>
      <view v-if="apt.confirmed_at" class="row">
        <text class="label">确认时间</text>
        <text class="value">{{ apt.confirmed_at }}</text>
      </view>
      <view v-if="apt.notes" class="row">
        <text class="label">备注</text>
        <text class="value">{{ apt.notes }}</text>
      </view>
      <view class="row">
        <text class="label">创建时间</text>
        <text class="value">{{ apt.created_at || "-" }}</text>
      </view>

      <view class="actions">
        <text v-if="apt.status === 'pending' && !isCounselor" class="cancel-btn" @click="cancelApt(apt.id)">
          取消预约
        </text>
        <text v-if="apt.status === 'pending' && isCounselor" class="confirm-btn" @click="confirmApt(apt.id)">
          确认预约
        </text>
        <text v-if="(apt.status === 'pending' || apt.status === 'confirmed') && isCounselor" class="cancel-btn" @click="cancelApt(apt.id)">
          取消
        </text>
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

onMounted(async () => {
  await loadAppointments();
});

async function loadAppointments() {
  try {
    appointments.value = await getMyAppointments();
  } catch (e) {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
}

function formatTime(t: string) {
  return t ? t.slice(0, 5) : "";
}

function statusLabel(s: string) {
  const m: Record<string, string> = {
    pending: "待确认",
    confirmed: "已确认",
    completed: "已完成",
    cancelled: "已取消",
  };
  return m[s] || s;
}

function statusClass(s: string) {
  return s === "confirmed" ? "confirmed"
    : s === "pending" ? "pending"
    : s === "cancelled" ? "cancelled"
    : "done";
}

async function cancelApt(id: number) {
  uni.showModal({
    title: "确认取消",
    content: "确定取消此预约吗？",
    success: async (res) => {
      if (!res.confirm) return;
      try {
        await cancelAppointment(id);
        uni.showToast({ title: "已取消", icon: "success" });
        await loadAppointments();
      } catch (e: any) {
        uni.showToast({ title: e.detail || "取消失败", icon: "none" });
      }
    },
  });
}

async function confirmApt(id: number) {
  uni.showModal({
    title: "确认预约",
    content: "确定确认此预约吗？确认后来访者将收到通知。",
    success: async (res) => {
      if (!res.confirm) return;
      try {
        await confirmAppointment(id);
        uni.showToast({ title: "预约已确认，来访者将收到通知", icon: "success", duration: 2000 });
        await loadAppointments();
      } catch (e: any) {
        uni.showToast({ title: e.detail || "操作失败", icon: "none" });
      }
    },
  });
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.page-title { font-size: 20px; font-weight: bold; color: #303133; margin-bottom: 16px; display: block; }
.empty { text-align: center; color: #909399; padding: 40px 0; font-size: 14px; }

.card { background: #fff; padding: 16px; border-radius: 10px; margin-bottom: 10px; }
.card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.status-tag { font-size: 13px; padding: 3px 12px; border-radius: 12px; font-weight: 500; }
.status-tag.pending { color: #e6a23c; background: #fdf6ec; }
.status-tag.confirmed { color: #409eff; background: #ecf5ff; }
.status-tag.done { color: #67c23a; background: #f0f9eb; }
.status-tag.cancelled { color: #909399; background: #f4f4f5; }
.visitor-name { font-size: 13px; color: #606266; }
.counselor-name { font-size: 13px; color: #606266; }

.row { display: flex; margin-bottom: 8px; }
.label { width: 70px; font-size: 13px; color: #909399; flex-shrink: 0; }
.value { font-size: 14px; color: #303133; }

.actions { margin-top: 12px; display: flex; justify-content: flex-end; gap: 16px; }
.confirm-btn { font-size: 14px; color: #fff; background: #67c23a; padding: 6px 16px; border-radius: 6px; }
.cancel-btn { font-size: 13px; color: #f56c6c; padding: 6px 0; }
</style>