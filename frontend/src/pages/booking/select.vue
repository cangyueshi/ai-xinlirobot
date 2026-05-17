<template>
  <view class="container">
    <text class="page-title">咨询师：{{ counselorName }}</text>

    <view class="date-picker">
      <text class="label">选择日期</text>
      <picker mode="date" :value="selectedDate" @change="onDateChange">
        <view class="picker-val">{{ selectedDate || "点击选择日期" }}</view>
      </picker>
    </view>

    <text class="sub-title">可选时间段</text>
    <view v-if="slots.length === 0" class="empty">该日期暂无可用时间段</view>

    <view
      v-for="slot in slots"
      :key="slot.id"
      class="slot-card"
      @click="bookSlot(slot)"
    >
      <view class="time-box">
        <text class="time">{{ slot.start_time }} - {{ slot.end_time }}</text>
      </view>
      <text class="action">预约</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getCounselorAvailabilities, bookAppointment } from "@/api/appointment";

const counselorId = ref(0);
const counselorName = ref("");
const selectedDate = ref("");
const slots = ref<any[]>([]);

onMounted(() => {
  const pages = getCurrentPages();
  const options = pages[pages.length - 1].options as any;
  counselorId.value = Number(options.counselorId);
  counselorName.value = options.name || "未知";
});

function onDateChange(e: any) {
  selectedDate.value = e.detail.value;
  loadSlots();
}

async function loadSlots() {
  if (!selectedDate.value) return;
  try {
    slots.value = await getCounselorAvailabilities(counselorId.value, selectedDate.value);
  } catch (e) {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
}

async function bookSlot(slot: any) {
  uni.showModal({
    title: "确认预约",
    content: `确定预约 ${slot.date} ${slot.start_time}-${slot.end_time} 吗？`,
    success: async (res) => {
      if (!res.confirm) return;
      try {
        await bookAppointment(slot.id);
        uni.showToast({ title: "预约成功", icon: "success" });
        setTimeout(() => uni.navigateBack(), 1000);
      } catch (e: any) {
        uni.showToast({ title: e.detail || "预约失败", icon: "none" });
      }
    },
  });
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.page-title { font-size: 20px; font-weight: bold; color: #303133; margin-bottom: 16px; display: block; }
.date-picker { background: #fff; padding: 14px 16px; border-radius: 10px; margin-bottom: 16px; display: flex; align-items: center; }
.label { font-size: 14px; color: #606266; margin-right: 12px; }
.picker-val { flex: 1; padding: 8px 12px; border: 1px solid #dcdfe6; border-radius: 6px; font-size: 14px; color: #409eff; }
.sub-title { font-size: 16px; font-weight: bold; color: #303133; margin-bottom: 10px; display: block; }
.empty { text-align: center; color: #909399; padding: 30px 0; font-size: 14px; }
.slot-card { display: flex; align-items: center; background: #fff; padding: 16px; border-radius: 8px; margin-bottom: 8px; }
.time-box { flex: 1; }
.time { font-size: 15px; color: #303133; font-weight: 500; }
.action { font-size: 14px; color: #fff; background: #67c23a; padding: 6px 18px; border-radius: 6px; }
</style>