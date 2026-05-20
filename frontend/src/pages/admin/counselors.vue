<template>
  <view class="page">
    <view class="header">
      <text class="page-title">咨询师管理</text>
      <text class="page-count">共 {{ counselors.length }} 人</text>
      <view class="header-actions">
        <button class="add-btn" @click="openAddForm">+ 添加咨询师</button>
      </view>
    </view>

    <view v-if="counselors.length === 0" class="empty">
      <text class="empty-icon">👩‍⚕️</text>
      <text class="empty-text">暂无咨询师</text>
    </view>

    <!-- 咨询师列表 -->
    <view v-for="c in counselors" :key="c.id" class="card" @click="openEditForm(c)">
      <view class="card-header">
        <view class="card-avatar" :style="{ background: avatarColor(c.display_name) }">
          <text>{{ c.display_name.charAt(0) }}</text>
        </view>
        <view class="card-info">
          <text class="card-name">{{ c.display_name }}</text>
          <text class="card-username">{{ c.username }}</text>
        </view>
        <text class="card-status" :class="c.status">
          {{ statusLabel(c) }}
        </text>
      </view>

      <view class="card-details">
        <text v-if="c.specialties" class="detail-item">擅长: {{ c.specialties }}</text>
        <text v-if="c.bio" class="detail-item">简介: {{ c.bio }}</text>
        <text v-if="c.email" class="detail-item">邮箱: {{ c.email }}</text>
      </view>

      <view class="card-actions">
        <text class="action-btn" @click.stop="resetPwd(c)">重置密码</text>
        <text v-if="c.status === 'active' && !c.is_approved" class="action-btn ok" @click.stop="doApprove(c)">通过审核</text>
        <text v-if="c.status === 'active' && !c.is_approved" class="action-btn danger" @click.stop="doReject(c)">拒绝</text>
        <text v-if="c.status === 'active' && c.is_approved" class="action-btn warn" @click.stop="toggleStatus(c, 'disable')">禁用</text>
        <text v-if="c.status === 'disabled'" class="action-btn ok" @click.stop="toggleStatus(c, 'enable')">启用</text>
        <text v-if="c.status !== 'deleted'" class="action-btn danger" @click.stop="remove(c)">删除</text>
      </view>
    </view>

    <!-- 添加/编辑弹窗 -->
    <view v-if="showForm" class="modal-mask" @click="closeForm">
      <view class="modal" @click.stop>
        <text class="modal-title">{{ isEditing ? '编辑咨询师' : '添加咨询师' }}</text>

        <text class="field-label">姓名</text>
        <input class="input" v-model="form.display_name" placeholder="请输入姓名" />

        <text class="field-label">登录账号</text>
        <input class="input" v-model="form.username" placeholder="请输入登录账号" :disabled="isEditing" />

        <text class="field-label">{{ isEditing ? '新密码（留空不修改）' : '登录密码' }}</text>
        <input class="input" v-model="form.password" type="password" :placeholder="isEditing ? '留空则不修改密码' : '至少6位密码'" />

        <text class="field-label">邮箱</text>
        <input class="input" v-model="form.email" placeholder="选填" />

        <text class="field-label">擅长领域</text>
        <input class="input" v-model="form.specialties" placeholder="如: 焦虑、抑郁、人际关系" />

        <text class="field-label">简介</text>
        <textarea class="input textarea" v-model="form.bio" placeholder="咨询师简介，选填" />

        <view class="modal-actions">
          <button class="btn-cancel" @click="closeForm">取消</button>
          <button class="btn-confirm" @click="doSave">{{ isEditing ? '保存修改' : '确认创建' }}</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import {
  getCounselors, createCounselor, updateCounselor,
  resetCounselorPassword, disableCounselor, enableCounselor, deleteCounselor,
  approveCounselor, rejectCounselor,
} from "@/api/admin";

const counselors = ref<any[]>([]);
const showForm = ref(false);
const isEditing = ref(false);
const editingId = ref(0);
const form = ref({
  display_name: "", username: "", password: "",
  email: "", specialties: "", bio: "",
});

const avatarColors = ["#5b8c7e", "#c97b63", "#6b9ac4", "#b88cb0", "#d4a56a"];

function avatarColor(name: string) {
  return avatarColors[name.charCodeAt(0) % avatarColors.length];
}

onMounted(loadData);

async function loadData() {
  try { counselors.value = await getCounselors(); } catch {}
}

function openAddForm() {
  isEditing.value = false;
  editingId.value = 0;
  form.value = { display_name: "", username: "", password: "", email: "", specialties: "", bio: "" };
  showForm.value = true;
}

function openEditForm(c: any) {
  isEditing.value = true;
  editingId.value = c.id;
  form.value = {
    display_name: c.display_name || "",
    username: c.username || "",
    password: "",
    email: c.email || "",
    specialties: c.specialties || "",
    bio: c.bio || "",
  };
  showForm.value = true;
}

function closeForm() {
  showForm.value = false;
}

async function doSave() {
  if (!form.value.display_name || !form.value.username) {
    uni.showToast({ title: "请填写姓名和账号", icon: "none" });
    return;
  }

  if (!isEditing.value && !form.value.password) {
    uni.showToast({ title: "请设置密码", icon: "none" });
    return;
  }

  try {
    if (isEditing.value) {
      await updateCounselor(editingId.value, {
        display_name: form.value.display_name,
        email: form.value.email || undefined,
        specialties: form.value.specialties || undefined,
        bio: form.value.bio || undefined,
      });
      if (form.value.password) {
        await resetCounselorPassword(editingId.value, form.value.password);
      }
      uni.showToast({ title: "修改已保存", icon: "success" });
    } else {
      await createCounselor(form.value);
      uni.showToast({ title: "创建成功", icon: "success" });
    }
    closeForm();
    loadData();
  } catch (e: any) {
    uni.showToast({ title: e.detail || "操作失败", icon: "none" });
  }
}

async function resetPwd(c: any) {
  const { confirm } = await uni.showModal({
    title: "重置密码",
    content: `确定重置 ${c.display_name} 的密码为 reset123456 吗？`,
  });
  if (!confirm) return;
  try {
    await resetCounselorPassword(c.id, "reset123456");
    uni.showToast({ title: "已重置为 reset123456", icon: "success" });
  } catch {}
}

function statusLabel(c: any) {
  if (c.status === 'deleted') return '已删除';
  if (c.status === 'disabled') return '已禁用';
  if (!c.is_approved) return '待审核';
  return '正常';
}

async function toggleStatus(c: any, action: string) {
  const label = action === 'disable' ? '禁用' : '启用';
  const { confirm } = await uni.showModal({ title: `确认${label}`, content: `确定${label}此账号吗？` });
  if (!confirm) return;
  try {
    if (action === 'disable') await disableCounselor(c.id);
    else await enableCounselor(c.id);
    uni.showToast({ title: `已${label}`, icon: "success" });
    loadData();
  } catch {}
}

async function doApprove(c: any) {
  const { confirm } = await uni.showModal({ title: '通过审核', content: `确定通过 ${c.display_name} 的审核吗？通过后来访者即可预约该咨询师。` });
  if (!confirm) return;
  try {
    await approveCounselor(c.id);
    uni.showToast({ title: '已通过审核', icon: 'success' });
    loadData();
  } catch {}
}

async function doReject(c: any) {
  const { confirm } = await uni.showModal({ title: '拒绝审核', content: `确定拒绝 ${c.display_name} 的申请吗？该账号将被禁用。` });
  if (!confirm) return;
  try {
    await rejectCounselor(c.id);
    uni.showToast({ title: '已拒绝', icon: 'success' });
    loadData();
  } catch {}
}

async function remove(c: any) {
  const { confirm } = await uni.showModal({
    title: "确认删除",
    content: `确定删除 ${c.display_name} 吗？（数据将保留）`,
  });
  if (!confirm) return;
  try {
    await deleteCounselor(c.id);
    uni.showToast({ title: "已删除", icon: "success" });
    loadData();
  } catch {}
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
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
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
  margin-right: auto;
}

.add-btn {
  background: $primary;
  color: #fff;
  font-size: 13px;
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  font-weight: 500;
}

.add-btn:active {
  opacity: 0.85;
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

.card:active {
  transform: scale(0.99);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.card-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
}

.card-info {
  flex: 1;
}

.card-name {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
  display: block;
}

.card-username {
  font-size: 12px;
  color: $text-muted;
  display: block;
  margin-top: 1px;
}

.card-status {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 6px;
  font-weight: 500;
}
.card-status.active { color: #67c23a; background: #f0f9eb; }
.card-status.disabled { color: #e6a23c; background: #fdf6ec; }
.card-status.deleted { color: #f56c6c; background: #fef0f0; }
.card-status:not(.active):not(.disabled):not(.deleted) { color: #909399; background: #f4f4f5; }

.card-details {
  margin-bottom: 10px;
}

.detail-item {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  line-height: 1.6;
}

.card-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.action-btn {
  font-size: 13px;
  color: $primary;
}

.action-btn.warn { color: #e6a23c; }
.action-btn.ok { color: #67c23a; }
.action-btn.danger { color: #f56c6c; }

.modal-mask {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(44, 62, 80, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  overflow-y: auto;
  padding: 20px 0;
}

.modal {
  width: 88%;
  max-width: 380px;
  max-height: 85vh;
  overflow-y: auto;
  background: #fff;
  border-radius: 18px;
  padding: 24px;
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: $text-primary;
  display: block;
  margin-bottom: 18px;
}

.field-label {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
}

.input {
  width: 100%;
  height: 40px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 0 12px;
  margin-bottom: 12px;
  font-size: 14px;
  box-sizing: border-box;
  background: #fafafa;
}

.input:focus {
  border-color: $primary;
  background: #fff;
}

.textarea {
  height: 70px;
  padding: 10px 12px;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 16px;
}

.btn-cancel {
  background: #f0f0f0;
  color: $text-secondary;
  font-size: 14px;
  padding: 10px 24px;
  border-radius: 8px;
  border: none;
}

.btn-confirm {
  background: $primary;
  color: #fff;
  font-size: 14px;
  padding: 10px 24px;
  border-radius: 8px;
  border: none;
  font-weight: 500;
}

.btn-confirm:active { opacity: 0.85; }
.btn-cancel:active { background: #e5e5e5; }
</style>
