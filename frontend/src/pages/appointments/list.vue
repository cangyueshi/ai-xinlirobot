<template>
  <view class="container">
    <text class="page-title">
      {{ isCounselor ? "来访者预约" : "我的预约" }}
    </text>

    <view v-if="appointments.length === 0" class="empty">暂无预约记录</view>

    <view v-for="apt in appointments" :key="apt.id" class="card">
      <view class="row">
        <text class="label">日期</text>
        <text class="value">{{ apt.date }}</text>
      </view>
      <view class="row">
        <text class="label">时间</text>
        <text class="value">{{ apt.start_time }} - {{ apt.end_time }}</text>
      </view>
      <view class="row">
        <text class="label">状态</text>
        <text class="value">
          <text class="status-tag" :class="statusClass(apt.status)">
            {{ statusLabel(apt.status) }}
          </text>
        </text>
      </view>
      <view v-if="apt.status === 'booked'" class="actions">
        <text class="cancel-btn" @click="cancelApt(apt.id)">取消预约</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useUserStore } from "@/store/user";
import { getMyAppointments, cancelAppointment } from "@/api/appointment";

const userStore = useUserStore();
const appointments = ref<any[]>([]);
const isCounselor = computed(() => userStore.userInfo?.role === "counselor");

onMounted(async () => {
  try {
    appointments.value = await getMyAppointments();
  } catch (e) {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
});

function statusLabel(s: string) {
  const m: Record<string, string> = { booked: "已预约", completed: "已完成", cancelled: "已取消" };
  return m[s] || s;
}

function statusClass(s: string) {
  return s === "booked" ? "active" : s === "cancelled" ? "cancelled" : "done";
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
        appointments.value = await getMyAppointments();
      } catch (e: any) {
        uni.showToast({ title: e.detail || "取消失败", icon: "none" });
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
.row { display: flex; margin-bottom: 8px; }
.label { width: 50px; font-size: 13px; color: #909399; }
.value { font-size: 14px; color: #303133; }
.status-tag { font-size: 12px; padding: 2px 10px; border-radius: 4px; }
.status-tag.active { color: #409eff; background: #ecf5ff; }
.status-tag.done { color: #67c23a; background: #f0f9eb; }
.status-tag.cancelled { color: #909399; background: #f4f4f5; }
.actions { margin-top: 10px; text-align: right; }
.cancel-btn { font-size: 13px; color: #f56c6c; padding: 4px 0; }
</style>