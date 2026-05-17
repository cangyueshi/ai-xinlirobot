<template>
  <view class="container">
    <view class="section">
      <text class="section-title">设置可预约时间</text>
      <view class="date-picker">
        <text class="label">选择日期</text>
        <picker mode="date" :value="selectedDate" @change="onDateChange">
          <view class="picker-val">{{ selectedDate || "点击选择日期" }}</view>
        </picker>
      </view>
    </view>

    <view v-if="selectedDate" class="section">
      <text class="section-title">时间段选择</text>
      <text class="weekday-hint">{{ weekdayHint }}</text>

      <view class="period-group">
        <text class="period-label">上午 9:00 - 12:00</text>
        <view class="slot-grid">
          <view
            v-for="slot in morningSlots"
            :key="slot.startTime"
            class="slot-item"
            :class="{ active: slot.selected }"
            @click="toggleSlot(slot)"
          >
            <text class="slot-time">{{ formatSlotLabel(slot) }}</text>
            <text class="slot-check">{{ slot.selected ? "✓" : "+" }}</text>
          </view>
        </view>
      </view>

      <view class="period-group">
        <text class="period-label">下午 12:30 - 16:30</text>
        <view class="slot-grid">
          <view
            v-for="slot in afternoonSlots"
            :key="slot.startTime"
            class="slot-item"
            :class="{ active: slot.selected }"
            @click="toggleSlot(slot)"
          >
            <text class="slot-time">{{ formatSlotLabel(slot) }}</text>
            <text class="slot-check">{{ slot.selected ? "✓" : "+" }}</text>
          </view>
        </view>
      </view>

      <view class="period-group">
        <text class="period-label">晚上 19:00 - 20:00</text>
        <view class="slot-grid">
          <view
            v-for="slot in eveningSlots"
            :key="slot.startTime"
            class="slot-item"
            :class="{ active: slot.selected }"
            @click="toggleSlot(slot)"
          >
            <text class="slot-time">{{ formatSlotLabel(slot) }}</text>
            <text class="slot-check">{{ slot.selected ? "✓" : "+" }}</text>
          </view>
        </view>
      </view>

      <button class="btn" @click="submitSlots">保存设置</button>
    </view>

    <view class="section">
      <text class="section-title">已设置的可用时段</text>
      <view class="date-selector">
        <picker mode="date" :value="viewDate" @change="onViewDateChange">
          <view class="picker-val">{{ viewDate || "选择日期查看" }}</view>
        </picker>
      </view>
      <view v-if="existingSlots.length === 0" class="empty">该日期暂无已设置的时段</view>
      <view v-for="av in existingSlots" :key="av.id" class="existing-item" :class="{ booked: av.is_booked }">
        <text class="existing-time">{{ av.start_time }} - {{ av.end_time }}</text>
        <text v-if="av.is_booked" class="tag-booked">已预约</text>
        <text v-else class="tag-free">空闲</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { setAvailabilities, getMyAvailabilities } from "@/api/appointment";

interface SlotItem {
  startTime: string;
  endTime: string;
  selected: boolean;
}

const selectedDate = ref("");
const viewDate = ref("");
const existingSlots = ref<any[]>([]);

const allSlots = ref<SlotItem[]>([
  { startTime: "09:00:00", endTime: "10:00:00", selected: false },
  { startTime: "10:00:00", endTime: "11:00:00", selected: false },
  { startTime: "11:00:00", endTime: "12:00:00", selected: false },
  { startTime: "12:30:00", endTime: "13:30:00", selected: false },
  { startTime: "13:30:00", endTime: "14:30:00", selected: false },
  { startTime: "14:30:00", endTime: "15:30:00", selected: false },
  { startTime: "15:30:00", endTime: "16:30:00", selected: false },
  { startTime: "19:00:00", endTime: "20:00:00", selected: false },
]);

const morningSlots = computed(() => allSlots.value.slice(0, 3));
const afternoonSlots = computed(() => allSlots.value.slice(3, 7));
const eveningSlots = computed(() => allSlots.value.slice(7, 8));

const weekdayHint = computed(() => {
  if (!selectedDate.value) return "";
  const d = new Date(selectedDate.value);
  const day = d.getDay();
  const names = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
  return names[day];
});

function formatSlotLabel(slot: SlotItem) {
  const s = slot.startTime.slice(0, 5);
  const e = slot.endTime.slice(0, 5);
  return `${s}-${e}`;
}

function toggleSlot(slot: SlotItem) {
  slot.selected = !slot.selected;
}

async function loadExistingSlots() {
  if (!viewDate.value) return;
  try {
    existingSlots.value = await getMyAvailabilities(viewDate.value);
  } catch (e) {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
}

function onDateChange(e: any) {
  selectedDate.value = e.detail.value;
  allSlots.value.forEach((s) => (s.selected = false));
}

function onViewDateChange(e: any) {
  viewDate.value = e.detail.value;
  loadExistingSlots();
}

async function submitSlots() {
  if (!selectedDate.value) {
    uni.showToast({ title: "请先选择日期", icon: "none" });
    return;
  }
  const selected = allSlots.value.filter((s) => s.selected);
  if (selected.length === 0) {
    uni.showToast({ title: "请至少选择一个时间段", icon: "none" });
    return;
  }
  try {
    await setAvailabilities({
      date: selectedDate.value,
      time_slots: selected.map((s) => ({
        start_time: s.startTime,
        end_time: s.endTime,
      })),
    });
    uni.showToast({ title: "设置成功", icon: "success" });
    allSlots.value.forEach((s) => (s.selected = false));
  } catch (e: any) {
    uni.showToast({ title: e.detail || "设置失败", icon: "none" });
  }
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.section { background: #fff; border-radius: 10px; padding: 16px; margin-bottom: 14px; }
.section-title { font-size: 17px; font-weight: bold; color: #303133; margin-bottom: 14px; display: block; }
.date-picker { display: flex; align-items: center; margin-bottom: 4px; }
.date-selector { margin-bottom: 12px; }
.label { width: 70px; font-size: 14px; color: #606266; }
.picker-val { flex: 1; padding: 8px 12px; border: 1px solid #dcdfe6; border-radius: 6px; font-size: 14px; color: #409eff; }
.weekday-hint { font-size: 13px; color: #909399; display: block; margin-bottom: 14px; }

.period-group { margin-bottom: 16px; }
.period-label { font-size: 14px; color: #606266; font-weight: 500; display: block; margin-bottom: 8px; }
.slot-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.slot-item {
  display: flex; align-items: center; justify-content: center;
  padding: 10px 14px; border-radius: 8px;
  border: 1px solid #dcdfe6; background: #fafafa;
  min-width: 100px;
}
.slot-item.active { border-color: #67c23a; background: #f0f9eb; }
.slot-time { font-size: 13px; color: #303133; }
.slot-item.active .slot-time { color: #67c23a; }
.slot-check { font-size: 14px; margin-left: 6px; color: #c0c4cc; }
.slot-item.active .slot-check { color: #67c23a; }

.btn { width: 100%; height: 44px; line-height: 44px; background: #409eff; color: #fff; border-radius: 8px; font-size: 16px; margin-top: 8px; border: none; }

.empty { text-align: center; color: #909399; padding: 30px 0; font-size: 14px; }
.existing-item { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #f0f0f0; }
.existing-item.booked { opacity: 0.6; }
.existing-time { flex: 1; font-size: 14px; color: #303133; }
.tag-booked { font-size: 12px; color: #e6a23c; background: #fdf6ec; padding: 2px 8px; border-radius: 4px; }
.tag-free { font-size: 12px; color: #67c23a; background: #f0f9eb; padding: 2px 8px; border-radius: 4px; }
</style>