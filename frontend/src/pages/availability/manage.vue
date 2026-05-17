<template>
  <view class="container">
    <view class="section">
      <text class="section-title">添加可预约时间段</text>
      <view class="form-row">
        <text class="label">日期</text>
        <picker mode="date" :value="form.date" @change="onDateChange">
          <view class="picker-val">{{ form.date || "选择日期" }}</view>
        </picker>
      </view>
      <view class="form-row">
        <text class="label">开始</text>
        <picker mode="time" :value="form.start_time" @change="onStartChange">
          <view class="picker-val">{{ form.start_time || "选择时间" }}</view>
        </picker>
      </view>
      <view class="form-row">
        <text class="label">结束</text>
        <picker mode="time" :value="form.end_time" @change="onEndChange">
          <view class="picker-val">{{ form.end_time || "选择时间" }}</view>
        </picker>
      </view>
      <button class="btn" @click="addSlot">添加时间段</button>
    </view>

    <view class="section">
      <text class="section-title">已设置的时间段 ({{ availabilities.length }})</text>
      <view v-if="availabilities.length === 0" class="empty">暂无可用时间段</view>
      <view
        v-for="av in availabilities"
        :key="av.id"
        class="slot-item"
        :class="{ booked: av.is_booked }"
      >
        <text class="slot-text">{{ av.date }} {{ av.start_time }}-{{ av.end_time }}</text>
        <text v-if="av.is_booked" class="tag-booked">已预约</text>
        <text v-else class="tag-free">空闲</text>
        <text v-if="!av.is_booked" class="del-btn" @click="removeSlot(av.id)">删除</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { addAvailability, getMyAvailabilities, deleteAvailability } from "@/api/appointment";

const availabilities = ref<any[]>([]);
const form = ref({ date: "", start_time: "", end_time: "" });

onMounted(() => loadAvailabilities());

async function loadAvailabilities() {
  try {
    availabilities.value = await getMyAvailabilities();
  } catch (e) {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
}

function onDateChange(e: any) {
  form.value.date = e.detail.value;
}
function onStartChange(e: any) {
  form.value.start_time = e.detail.value;
}
function onEndChange(e: any) {
  form.value.end_time = e.detail.value;
}

async function addSlot() {
  if (!form.value.date || !form.value.start_time || !form.value.end_time) {
    uni.showToast({ title: "请完整填写", icon: "none" });
    return;
  }
  try {
    await addAvailability({
      date: form.value.date,
      start_time: form.value.start_time,
      end_time: form.value.end_time,
    });
    uni.showToast({ title: "添加成功", icon: "success" });
    form.value = { date: "", start_time: "", end_time: "" };
    await loadAvailabilities();
  } catch (e: any) {
    uni.showToast({ title: e.detail || "添加失败", icon: "none" });
  }
}

async function removeSlot(id: number) {
  try {
    await deleteAvailability(id);
    uni.showToast({ title: "已删除", icon: "success" });
    await loadAvailabilities();
  } catch (e: any) {
    uni.showToast({ title: e.detail || "删除失败", icon: "none" });
  }
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.section { background: #fff; border-radius: 10px; padding: 16px; margin-bottom: 14px; }
.section-title { font-size: 17px; font-weight: bold; color: #303133; margin-bottom: 14px; display: block; }
.form-row { display: flex; align-items: center; margin-bottom: 12px; }
.label { width: 50px; font-size: 14px; color: #606266; }
.picker-val { flex: 1; padding: 8px 12px; border: 1px solid #dcdfe6; border-radius: 6px; font-size: 14px; color: #606266; }
.btn { width: 100%; height: 42px; line-height: 42px; background: #409eff; color: #fff; border-radius: 8px; font-size: 16px; margin-top: 6px; border: none; }
.empty { text-align: center; color: #909399; padding: 30px 0; font-size: 14px; }
.slot-item { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #f0f0f0; }
.slot-item.booked { opacity: 0.6; }
.slot-text { flex: 1; font-size: 14px; color: #303133; }
.tag-booked { font-size: 12px; color: #e6a23c; background: #fdf6ec; padding: 2px 8px; border-radius: 4px; }
.tag-free { font-size: 12px; color: #67c23a; background: #f0f9eb; padding: 2px 8px; border-radius: 4px; margin-right: 8px; }
.del-btn { font-size: 13px; color: #f56c6c; margin-left: 8px; }
</style>