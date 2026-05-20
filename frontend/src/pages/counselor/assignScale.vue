<template>
  <view class="page">
    <view class="header">
      <text class="page-title">分发量表</text>
      <text class="page-desc">选择来访者和量表，为其分配测评任务</text>
    </view>

    <!-- 选择题库 -->
    <view class="section">
      <text class="section-label">选择量表</text>
      <view
        v-for="s in scales"
        :key="s.id"
        class="scale-card"
        :class="{ selected: selectedScaleId === s.id }"
        @click="selectedScaleId = s.id"
      >
        <view class="scale-top">
          <text class="scale-name">{{ s.name }}</text>
          <text class="scale-count">{{ s.question_count }} 题</text>
        </view>
        <text class="scale-desc">{{ s.description }}</text>
        <view v-if="selectedScaleId === s.id" class="scale-check">
          <text class="check-icon">✓</text>
        </view>
      </view>
      <view v-if="scales.length === 0" class="empty">暂无可用量表</view>
    </view>

    <!-- 选择来访者 -->
    <view class="section">
      <text class="section-label">选择来访者</text>
      <view
        v-for="v in visitors"
        :key="v.id"
        class="visitor-card"
        :class="{ selected: selectedVisitorId === v.id }"
        @click="selectedVisitorId = v.id"
      >
        <view class="visitor-left">
          <view class="visitor-avatar" :style="{ background: avatarColor(v.display_name) }">
            <text class="avatar-text">{{ v.display_name.charAt(0) }}</text>
          </view>
        </view>
        <view class="visitor-body">
          <text class="visitor-name">{{ v.display_name }}</text>
          <text class="visitor-meta">对话 {{ v.chat_count }} 次 · 测评 {{ v.assessment_count }} 次</text>
        </view>
        <view v-if="selectedVisitorId === v.id" class="visitor-check">
          <text class="check-icon">✓</text>
        </view>
      </view>
      <view v-if="visitors.length === 0" class="empty">暂无来访者</view>
    </view>

    <!-- 提交按钮 -->
    <button
      class="submit-btn"
      :disabled="!selectedVisitorId || !selectedScaleId || submitting"
      @click="handleAssign"
    >
      {{ submitting ? "分配中..." : "确认分发" }}
    </button>

    <!-- 分配记录 -->
    <view class="section">
      <view class="section-header">
        <text class="section-label">已分发记录</text>
        <text class="assign-count">{{ assignments.length }} 条</text>
      </view>
      <view v-for="a in assignments" :key="a.id" class="assign-card">
        <view class="assign-info">
          <text class="assign-scale">{{ a.scale_name }}</text>
          <text class="assign-visitor">→ {{ a.visitor_name }}</text>
          <text class="assign-status" :class="a.status">
            {{ a.status === "completed" ? "已完成" : "待完成" }}
          </text>
        </view>
        <view class="assign-footer">
          <text class="assign-time">{{ fmtTime(a.created_at) }}</text>
          <text v-if="a.status === 'pending'" class="assign-delete" @click="handleDelete(a.id)">撤销</text>
        </view>
      </view>
      <view v-if="assignments.length === 0" class="empty">暂无分发记录</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import {
  getAllVisitors,
  getCounselorScales,
  getScaleAssignments,
  createScaleAssignment,
  deleteScaleAssignment,
  type VisitorInfo,
  type ScaleInfo,
  type ScaleAssignment,
} from "@/api/counselor";

const scales = ref<ScaleInfo[]>([]);
const visitors = ref<VisitorInfo[]>([]);
const assignments = ref<ScaleAssignment[]>([]);
const selectedScaleId = ref(0);
const selectedVisitorId = ref(0);
const submitting = ref(false);

const avatarColors = ["#5b8c7e", "#c97b63", "#6b9ac4", "#b88cb0", "#d4a56a", "#7aa89e"];

function avatarColor(name: string) {
  const idx = name.charCodeAt(0) % avatarColors.length;
  return avatarColors[idx];
}

function fmtTime(t: string | null) {
  if (!t) return "";
  return t.slice(0, 16).replace("T", " ");
}

onMounted(async () => {
  try {
    const [s, v, a] = await Promise.all([
      getCounselorScales(),
      getAllVisitors(),
      getScaleAssignments(),
    ]);
    scales.value = s;
    visitors.value = v;
    assignments.value = a;
  } catch {
    uni.showToast({ title: "加载数据失败", icon: "none" });
  }
});

async function handleAssign() {
  if (!selectedVisitorId.value || !selectedScaleId.value) return;
  submitting.value = true;
  try {
    await createScaleAssignment(selectedVisitorId.value, selectedScaleId.value);
    uni.showToast({ title: "分发成功", icon: "success" });
    assignments.value = await getScaleAssignments();
    selectedScaleId.value = 0;
    selectedVisitorId.value = 0;
  } catch (e: any) {
    uni.showToast({ title: e.detail || "分发失败", icon: "none" });
  } finally {
    submitting.value = false;
  }
}

async function handleDelete(id: number) {
  uni.showModal({
    title: "提示",
    content: "确定撤销该分发吗？",
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteScaleAssignment(id);
          uni.showToast({ title: "已撤销", icon: "success" });
          assignments.value = await getScaleAssignments();
        } catch {
          uni.showToast({ title: "撤销失败", icon: "none" });
        }
      }
    },
  });
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
  margin-bottom: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: $text-primary;
  display: block;
}

.page-desc {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-top: 4px;
}

.section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 10px;
}

.assign-count {
  font-size: 12px;
  color: $text-muted;
}

.scale-card {
  background: $card-bg;
  padding: 14px 16px;
  border-radius: 14px;
  margin-bottom: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  border: 1.5px solid transparent;
  position: relative;
}

.scale-card.selected {
  border-color: $primary;
  background: #f0f7f4;
}

.scale-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.scale-name {
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
}

.scale-count {
  font-size: 12px;
  color: $text-muted;
}

.scale-desc {
  font-size: 13px;
  color: $text-secondary;
  line-height: 1.5;
  display: block;
}

.scale-check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: $primary;
  display: flex;
  align-items: center;
  justify-content: center;
}

.check-icon {
  color: #fff;
  font-size: 13px;
  font-weight: bold;
}

.visitor-card {
  display: flex;
  align-items: center;
  background: $card-bg;
  padding: 12px 16px;
  border-radius: 14px;
  margin-bottom: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  border: 1.5px solid transparent;
  position: relative;
}

.visitor-card.selected {
  border-color: $primary;
  background: #f0f7f4;
}

.visitor-left {
  margin-right: 12px;
}

.visitor-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 16px;
  color: #fff;
  font-weight: 700;
}

.visitor-body {
  flex: 1;
}

.visitor-name {
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
  display: block;
}

.visitor-meta {
  font-size: 12px;
  color: $text-muted;
  display: block;
  margin-top: 2px;
}

.visitor-check {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: $primary;
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-btn {
  width: 100%;
  height: 46px;
  line-height: 46px;
  background: $primary;
  color: #fff;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  margin-bottom: 24px;
}

.submit-btn[disabled] {
  opacity: 0.5;
}

.assign-card {
  background: $card-bg;
  padding: 14px 16px;
  border-radius: 14px;
  margin-bottom: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

.assign-info {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}

.assign-scale {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
}

.assign-visitor {
  font-size: 13px;
  color: $text-secondary;
}

.assign-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.assign-status.pending {
  color: #e6a23c;
  background: #fdf6ec;
}

.assign-status.completed {
  color: #67c23a;
  background: #f0f9eb;
}

.assign-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.assign-time {
  font-size: 11px;
  color: $text-muted;
}

.assign-delete {
  font-size: 12px;
  color: #f56c6c;
}

.empty {
  text-align: center;
  padding: 30px 0;
  font-size: 13px;
  color: $text-muted;
}
</style>
