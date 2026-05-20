<template>
  <view class="page">
    <view class="header">
      <text class="page-title">次级管理员</text>
      <text class="page-count">共 {{ subs.length }} 人</text>
      <button class="add-btn" @click="openAddForm">+ 添加</button>
    </view>

    <view v-if="subs.length === 0" class="empty">
      <text class="empty-icon">👤</text>
      <text class="empty-text">暂无次级管理员</text>
    </view>

    <view v-for="s in subs" :key="s.id" class="card">
      <view class="card-header">
        <view class="card-avatar">
          <text>{{ s.display_name.charAt(0) }}</text>
        </view>
        <view class="card-info">
          <text class="card-name">{{ s.display_name }}</text>
          <text class="card-username">{{ s.username }}</text>
        </view>
      </view>

      <view v-if="s.sub_admin_permissions" class="perm-tags">
        <text
          v-for="p in parsePermissions(s.sub_admin_permissions)"
          :key="p"
          class="perm-tag"
        >{{ p }}</text>
      </view>

      <view class="card-actions">
        <text class="action-btn" @click="openEditForm(s)">编辑权限</text>
        <text class="action-btn danger" @click="remove(s)">删除</text>
      </view>
    </view>

    <!-- 添加/编辑弹窗 -->
    <view v-if="showForm" class="modal-mask" @click="closeForm">
      <view class="modal" @click.stop>
        <text class="modal-title">{{ isEditing ? '编辑权限' : '添加次级管理员' }}</text>

        <text class="field-label">姓名</text>
        <input class="input" v-model="form.display_name" placeholder="请输入姓名" />

        <text class="field-label">登录账号</text>
        <input class="input" v-model="form.username" placeholder="请输入登录账号" :disabled="isEditing" />

        <text class="field-label">{{ isEditing ? '新密码（留空不修改）' : '登录密码' }}</text>
        <input class="input" v-model="form.password" type="password" :placeholder="isEditing ? '留空则不修改' : '至少6位'" />

        <text class="field-label">邮箱</text>
        <input class="input" v-model="form.email" placeholder="选填" />

        <!-- 权限勾选 -->
        <text class="field-label" style="margin-top:4px;">权限设置</text>
        <view class="perm-checkboxes">
          <view
            v-for="perm in allPermissions"
            :key="perm.key"
            class="perm-checkbox"
            :class="{ checked: selectedPerms.includes(perm.key) }"
            @click="togglePerm(perm.key)"
          >
            <view class="checkbox-box">
              <text v-if="selectedPerms.includes(perm.key)">✓</text>
            </view>
            <view class="checkbox-info">
              <text class="checkbox-label">{{ perm.label }}</text>
              <text class="checkbox-desc">{{ perm.desc }}</text>
            </view>
          </view>
        </view>

        <view class="modal-actions">
          <button class="btn-cancel" @click="closeForm">取消</button>
          <button class="btn-confirm" @click="doSave">{{ isEditing ? '保存' : '创建' }}</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getSubAdmins, createSubAdmin, updateSubAdmin, deleteSubAdmin } from "@/api/admin";

const subs = ref<any[]>([]);
const showForm = ref(false);
const isEditing = ref(false);
const editingId = ref(0);
const form = ref({ display_name: "", username: "", password: "", email: "" });
const selectedPerms = ref<string[]>([]);

const allPermissions = [
  { key: "counselor_mgmt",  label: "咨询师管理",  desc: "添加、编辑、禁用咨询师" },
  { key: "visitor_mgmt",    label: "来访者管理",  desc: "查看来访者信息" },
  { key: "chat_review",     label: "对话审核",    desc: "查看所有对话记录" },
  { key: "assessment_view", label: "测评查看",    desc: "查看测评结果" },
  { key: "data_export",     label: "数据导出",    desc: "导出统计数据" },
];

onMounted(loadData);

async function loadData() {
  try { subs.value = await getSubAdmins(); } catch {}
}

function parsePermissions(permissions: string): string[] {
  if (!permissions) return [];
  const permLabels: Record<string, string> = {
    counselor_mgmt: "咨询师管理",
    visitor_mgmt: "来访者管理",
    chat_review: "对话审核",
    assessment_view: "测评查看",
    data_export: "数据导出",
  };
  return permissions.split(",").map((k) => permLabels[k.trim()] || k.trim());
}

function openAddForm() {
  isEditing.value = false;
  editingId.value = 0;
  form.value = { display_name: "", username: "", password: "", email: "" };
  selectedPerms.value = [];
  showForm.value = true;
}

function openEditForm(s: any) {
  isEditing.value = true;
  editingId.value = s.id;
  form.value = {
    display_name: s.display_name || "",
    username: s.username || "",
    password: "",
    email: s.email || "",
  };
  selectedPerms.value = s.sub_admin_permissions
    ? s.sub_admin_permissions.split(",").map((k: string) => k.trim()).filter(Boolean)
    : [];
  showForm.value = true;
}

function closeForm() {
  showForm.value = false;
}

function togglePerm(key: string) {
  const idx = selectedPerms.value.indexOf(key);
  if (idx >= 0) {
    selectedPerms.value.splice(idx, 1);
  } else {
    selectedPerms.value.push(key);
  }
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

  const payload = {
    ...form.value,
    permissions: selectedPerms.value.join(","),
  };

  try {
    if (isEditing.value) {
      await updateSubAdmin(editingId.value, payload);
      uni.showToast({ title: "已保存", icon: "success" });
    } else {
      await createSubAdmin(payload);
      uni.showToast({ title: "创建成功", icon: "success" });
    }
    closeForm();
    loadData();
  } catch (e: any) {
    uni.showToast({ title: e.detail || "操作失败", icon: "none" });
  }
}

async function remove(s: any) {
  const { confirm } = await uni.showModal({
    title: "确认删除",
    content: `确定删除 ${s.display_name} 吗？`,
  });
  if (!confirm) return;
  try {
    await deleteSubAdmin(s.id);
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

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.card-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: #6b9ac4;
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

.perm-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.perm-tag {
  font-size: 11px;
  color: $primary;
  background: #e8f0ed;
  padding: 3px 10px;
  border-radius: 6px;
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

.perm-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 8px 0;
}

.perm-checkbox {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 10px;
  border: 1.5px solid #e8e8e8;
  transition: all 0.15s;
}

.perm-checkbox.checked {
  border-color: $primary;
  background: #f0f7f4;
}

.checkbox-box {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  border: 2px solid #d0d5d5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
  font-size: 12px;
  color: #fff;
  transition: all 0.15s;
}

.perm-checkbox.checked .checkbox-box {
  background: $primary;
  border-color: $primary;
  color: #fff;
}

.checkbox-info {
  flex: 1;
}

.checkbox-label {
  font-size: 14px;
  font-weight: 500;
  color: $text-primary;
  display: block;
}

.checkbox-desc {
  font-size: 12px;
  color: $text-muted;
  display: block;
  margin-top: 1px;
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
</style>
