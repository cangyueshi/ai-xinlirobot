<template>
  <view class="container">
    <text class="page-title">咨询师：{{ counselorName }}</text>

    <view class="date-picker">
      <text class="label">选择日期</text>
      <picker mode="date" :value="selectedDate" @change="onDateChange">
        <view class="picker-val">{{ selectedDate || "点击选择日期" }}</view>
      </picker>
    </view>

    <view v-if="selectedDate">
      <view v-if="slots.length === 0" class="empty">该日期暂无可用时间段</view>

      <view v-else>
        <view class="hint-section">
          <view class="hint-row">
            <view class="hint-dot primary"></view>
            <text class="hint-text">首选时间段（必选）</text>
          </view>
          <view class="hint-row">
            <view class="hint-dot backup"></view>
            <text class="hint-text">备选时间段（可选）</text>
          </view>
        </view>

        <view class="sub-title">可选时间段</view>
        <view
          v-for="slot in sortedSlots"
          :key="slot.id"
          class="slot-card"
          :class="{
            primary: primarySlot?.id === slot.id,
            backup: backupSlot?.id === slot.id,
          }"
          @click="selectSlot(slot)"
        >
          <view class="time-box">
            <text class="time">{{ slot.date }} {{ formatTime(slot.start_time) }} - {{ formatTime(slot.end_time) }}</text>
          </view>
          <text v-if="primarySlot?.id === slot.id" class="tag tag-primary">首选</text>
          <text v-else-if="backupSlot?.id === slot.id" class="tag tag-backup">备选</text>
        </view>

        <view class="confirm-area">
          <text class="confirm-hint" v-if="!primarySlot">请先选择首选时间段</text>
          <button class="btn-confirm" :disabled="!primarySlot" @click="confirmBook">
            确认提交
          </button>
        </view>
      </view>
    </view>

    <view v-else class="empty">请先选择日期</view>
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

onLoad((options: any) => {
  counselorId.value = Number(options.counselorId);
  counselorName.value = options.name || "未知";
});

function onDateChange(e: any) {
  selectedDate.value = e.detail.value;
  primarySlot.value = null;
  backupSlot.value = null;
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
    if (primarySlot.value && backupSlot.value) {
      primarySlot.value = slot;
      backupSlot.value = null;
    }
  }
}

async function confirmBook() {
  if (!primarySlot.value) {
    uni.showToast({ title: "请选择首选时间段", icon: "none" });
    return;
  }

  const primaryTime = `${formatTime(primarySlot.value.start_time)}-${formatTime(primarySlot.value.end_time)}`;
  let content = `确认预约 ${primaryTime} 吗？`;
  if (backupSlot.value) {
    const backupTime = `${formatTime(backupSlot.value.start_time)}-${formatTime(backupSlot.value.end_time)}`;
    content += `\n备选时间段：${backupTime}`;
  }

  uni.showModal({
    title: "确认预约",
    content,
    success: async (res) => {
      if (!res.confirm) return;
      try {
        await bookAppointment({
          availability_id: primarySlot.value.id,
          backup_availability_id: backupSlot.value?.id || undefined,
        });
        uni.showToast({ title: "预约已提交，等待咨询师确认", icon: "success", duration: 2000 });
        setTimeout(() => uni.navigateBack(), 2000);
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

.hint-section { background: #fff; border-radius: 10px; padding: 14px 16px; margin-bottom: 12px; }
.hint-row { display: flex; align-items: center; margin-bottom: 8px; }
.hint-row:last-child { margin-bottom: 0; }
.hint-dot { width: 14px; height: 14px; border-radius: 4px; margin-right: 8px; flex-shrink: 0; }
.hint-dot.primary { background: #409eff; }
.hint-dot.backup { background: #e6a23c; }
.hint-text { font-size: 13px; color: #606266; }

.sub-title { font-size: 16px; font-weight: bold; color: #303133; margin-bottom: 10px; display: block; }
.empty { text-align: center; color: #909399; padding: 40px 0; font-size: 14px; }

.slot-card {
  display: flex; align-items: center; background: #fff;
  padding: 14px 16px; border-radius: 8px; margin-bottom: 8px;
  border: 2px solid transparent;
}
.slot-card.primary { border-color: #409eff; background: #ecf5ff; }
.slot-card.backup { border-color: #e6a23c; background: #fdf6ec; }
.time-box { flex: 1; }
.time { font-size: 14px; color: #303133; }
.tag { font-size: 12px; padding: 3px 10px; border-radius: 4px; font-weight: 500; }
.tag-primary { color: #fff; background: #409eff; }
.tag-backup { color: #fff; background: #e6a23c; }

.confirm-area { margin-top: 20px; text-align: center; }
.confirm-hint { font-size: 13px; color: #f56c6c; display: block; margin-bottom: 10px; }
.btn-confirm { width: 80%; height: 46px; line-height: 46px; background: #67c23a; color: #fff; border-radius: 23px; font-size: 17px; font-weight: bold; border: none; }
.btn-confirm[disabled] { background: #c0c4cc; }
</style>