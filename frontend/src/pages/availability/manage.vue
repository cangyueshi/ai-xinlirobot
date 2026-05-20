<template>
  <view class="page">
    <!-- 设置模式切换 -->
    <view class="page-header">
      <text class="page-title">排班管理</text>
      <text class="page-sub">设置可预约时间段（至少提前两天）</text>
    </view>

    <view class="mode-tabs">
      <view
        class="mode-tab"
        :class="{ active: mode === 'single' }"
        @click="mode = 'single'"
      >单日设置</view>
      <view
        class="mode-tab"
        :class="{ active: mode === 'week' }"
        @click="mode = 'week'"
      >整周设置</view>
    </view>

    <!-- 单日模式 -->
    <view v-if="mode === 'single'" class="section-card">
      <text class="section-label">选择日期</text>
      <picker mode="date" :value="selectedDate" @change="onDateChange">
        <view class="picker-trigger">
          <text class="picker-text" :class="{ placeholder: !selectedDate }">
            {{ selectedDate || '点击选择日期' }}
          </text>
          <text class="picker-arrow">▼</text>
        </view>
      </picker>
      <text v-if="selectedDate" class="weekday-hint">{{ weekdayHint(selectedDate) }}</text>
    </view>

    <!-- 整周模式 -->
    <view v-if="mode === 'week'" class="section-card">
      <text class="section-label">选择周范围</text>
      <view class="week-range">
        <picker mode="date" :value="weekStart" @change="onWeekStartChange">
          <view class="picker-trigger">
            <text class="picker-text" :class="{ placeholder: !weekStart }">
              {{ weekStart || '开始日期' }}
            </text>
            <text class="picker-arrow">▼</text>
          </view>
        </picker>
        <text class="week-sep">至</text>
        <picker mode="date" :value="weekEnd" @change="onWeekEndChange">
          <view class="picker-trigger">
            <text class="picker-text" :class="{ placeholder: !weekEnd }">
              {{ weekEnd || '结束日期' }}
            </text>
            <text class="picker-arrow">▼</text>
          </view>
        </picker>
      </view>
      <text v-if="weekStart && weekEnd" class="weekday-hint">
        将统一设置所选日期范围内的所有工作日
      </text>
    </view>

    <!-- 时间段选择 -->
    <view v-if="hasDateSelected" class="section-card">
      <text class="section-label">选择可预约时间段</text>

      <view class="period-group">
        <text class="period-label">上午 <text class="period-range">9:00 - 12:00</text></text>
        <view class="slot-grid">
          <view
            v-for="slot in morningSlots"
            :key="slot.startTime"
            class="slot-item"
            :class="{ active: slot.selected }"
            @click="toggleSlot(slot)"
          >
            <text class="slot-time">{{ formatSlotLabel(slot) }}</text>
            <text class="slot-check">{{ slot.selected ? '✓' : '+' }}</text>
          </view>
        </view>
      </view>

      <view class="period-group">
        <text class="period-label">下午 <text class="period-range">12:30 - 16:30</text></text>
        <view class="slot-grid">
          <view
            v-for="slot in afternoonSlots"
            :key="slot.startTime"
            class="slot-item"
            :class="{ active: slot.selected }"
            @click="toggleSlot(slot)"
          >
            <text class="slot-time">{{ formatSlotLabel(slot) }}</text>
            <text class="slot-check">{{ slot.selected ? '✓' : '+' }}</text>
          </view>
        </view>
      </view>

      <view class="period-group">
        <text class="period-label">晚上 <text class="period-range">19:00 - 20:00</text></text>
        <view class="slot-grid">
          <view
            v-for="slot in eveningSlots"
            :key="slot.startTime"
            class="slot-item"
            :class="{ active: slot.selected }"
            @click="toggleSlot(slot)"
          >
            <text class="slot-time">{{ formatSlotLabel(slot) }}</text>
            <text class="slot-check">{{ slot.selected ? '✓' : '+' }}</text>
          </view>
        </view>
      </view>

      <button class="save-btn" @click="submitSlots">
        {{ mode === 'week' ? '批量设置整周排班' : '保存设置' }}
      </button>
    </view>

    <!-- 已设置时段 -->
    <view class="section-card">
      <view class="section-header">
        <text class="section-label">已设置的排班</text>
      </view>
      <picker mode="date" :value="viewDate" @change="onViewDateChange">
        <view class="picker-trigger">
          <text class="picker-text" :class="{ placeholder: !viewDate }">
            {{ viewDate || '选择日期查看' }}
          </text>
          <text class="picker-arrow">▼</text>
        </view>
      </picker>
      <view v-if="existingSlots.length === 0" class="empty-state">暂无已设置的时段</view>
      <view
        v-for="av in existingSlots"
        :key="av.id"
        class="exist-item"
        :class="{ booked: av.is_booked }"
      >
        <view class="exist-left">
          <text class="exist-time">{{ formatTime(av.start_time) }} - {{ formatTime(av.end_time) }}</text>
        </view>
        <text v-if="av.is_booked" class="exist-tag booked">已预约</text>
        <text v-else class="exist-tag free">空闲</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { setAvailabilities, getMyAvailabilities } from "@/api/appointment";

interface SlotItem {
  startTime: string;
  endTime: string;
  selected: boolean;
}

const mode = ref("single");
const selectedDate = ref("");
const weekStart = ref("");
const weekEnd = ref("");
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
const eveningSlots = computed(() => allSlots.value.slice(7));

const hasDateSelected = computed(() => {
  if (mode.value === "single") return !!selectedDate.value;
  return !!weekStart.value && !!weekEnd.value;
});

function weekdayHint(d: string) {
  if (!d) return "";
  const day = new Date(d).getDay();
  return ["周日", "周一", "周二", "周三", "周四", "周五", "周六"][day];
}

function formatSlotLabel(slot: SlotItem) {
  return `${slot.startTime.slice(0, 5)}-${slot.endTime.slice(0, 5)}`;
}

function formatTime(t: string) {
  return t ? t.slice(0, 5) : "";
}

function toggleSlot(slot: SlotItem) {
  slot.selected = !slot.selected;
}

function onDateChange(e: any) {
  selectedDate.value = e.detail.value;
  allSlots.value.forEach((s) => (s.selected = false));
}

function onWeekStartChange(e: any) {
  weekStart.value = e.detail.value;
  allSlots.value.forEach((s) => (s.selected = false));
}

function onWeekEndChange(e: any) {
  weekEnd.value = e.detail.value;
  allSlots.value.forEach((s) => (s.selected = false));
}

function onViewDateChange(e: any) {
  viewDate.value = e.detail.value;
  loadExistingSlots();
}

async function loadExistingSlots() {
  if (!viewDate.value) return;
  try {
    existingSlots.value = await getMyAvailabilities(viewDate.value);
  } catch {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
}

async function submitSlots() {
  const selected = allSlots.value.filter((s) => s.selected);
  if (selected.length === 0) {
    uni.showToast({ title: "请至少选择一个时间段", icon: "none" });
    return;
  }

  const timeSlots = selected.map((s) => ({
    start_time: s.startTime,
    end_time: s.endTime,
  }));

  try {
    if (mode.value === "single") {
      if (!selectedDate.value) {
        uni.showToast({ title: "请先选择日期", icon: "none" });
        return;
      }
      await setAvailabilities({ date: selectedDate.value, time_slots: timeSlots });
    } else {
      if (!weekStart.value || !weekEnd.value) {
        uni.showToast({ title: "请选择开始和结束日期", icon: "none" });
        return;
      }
      await setAvailabilities({
        date_range: [weekStart.value, weekEnd.value],
        time_slots: timeSlots,
      });
    }

    uni.showToast({ title: "设置成功", icon: "success" });
    allSlots.value.forEach((s) => (s.selected = false));
    if (viewDate.value) loadExistingSlots();
  } catch (e: any) {
    uni.showToast({ title: e.detail || "设置失败", icon: "none" });
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

.page-sub {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-top: 4px;
}

.mode-tabs {
  display: flex;
  background: $card-bg;
  border-radius: 12px;
  margin-bottom: 12px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

.mode-tab {
  flex: 1;
  text-align: center;
  padding: 12px 0;
  font-size: 14px;
  color: $text-muted;
  transition: all 0.2s;
}

.mode-tab.active {
  color: $primary;
  font-weight: 600;
  border-bottom: 2px solid $primary;
  background: #f0f7f4;
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.week-range {
  display: flex;
  align-items: center;
  gap: 10px;
}

.week-range .picker-trigger {
  flex: 1;
}

.week-sep {
  font-size: 14px;
  color: $text-muted;
  flex-shrink: 0;
}

.weekday-hint {
  font-size: 12px;
  color: $text-muted;
  display: block;
  margin-top: 8px;
}

.period-group {
  margin-bottom: 16px;
}

.period-label {
  font-size: 14px;
  color: $text-secondary;
  font-weight: 500;
  display: block;
  margin-bottom: 8px;
}

.period-range {
  font-weight: 400;
  color: $text-muted;
  font-size: 12px;
}

.slot-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.slot-item {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1.5px solid #e0e0e0;
  background: #fafafa;
  min-width: 96px;
  transition: all 0.15s;
}

.slot-item.active {
  border-color: $primary;
  background: #f0f7f4;
}

.slot-time {
  font-size: 13px;
  color: $text-secondary;
}

.slot-item.active .slot-time {
  color: $primary;
  font-weight: 600;
}

.slot-check {
  font-size: 14px;
  margin-left: 6px;
  color: #c0c4cc;
}

.slot-item.active .slot-check {
  color: $primary;
}

.save-btn {
  width: 100%;
  height: 44px;
  line-height: 44px;
  background: $primary;
  color: #fff;
  border-radius: 22px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  margin-top: 8px;
}

.save-btn:active {
  opacity: 0.85;
}

.empty-state {
  text-align: center;
  color: $text-muted;
  padding: 30px 0;
  font-size: 14px;
}

.exist-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.exist-item.booked {
  opacity: 0.6;
}

.exist-left {
  flex: 1;
}

.exist-time {
  font-size: 14px;
  color: $text-primary;
}

.exist-tag {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.exist-tag.booked {
  color: #d4a56a;
  background: #faf3ef;
}

.exist-tag.free {
  color: $primary;
  background: #f0f7f4;
}
</style>
