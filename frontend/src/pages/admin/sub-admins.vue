<template>
  <view class="container">
    <view class="header">
      <text class="page-title">次级管理员</text>
      <button class="add-btn" @click="showForm = true">+ 添加</button>
    </view>

    <view v-if="subs.length === 0" class="empty">暂无次级管理员</view>

    <view v-for="s in subs" :key="s.id" class="card">
      <text class="name">{{ s.display_name }}</text>
      <text class="info">账号: {{ s.username }}</text>
      <text v-if="s.permissions" class="info">权限: {{ s.permissions }}</text>
      <view class="actions">
        <text class="act danger" @click="remove(s)">删除</text>
      </view>
    </view>

    <view v-if="showForm" class="modal-mask" @click="showForm = false">
      <view class="modal" @click.stop>
        <text class="modal-title">添加次级管理员</text>
        <input class="input" v-model="form.display_name" placeholder="姓名" />
        <input class="input" v-model="form.username" placeholder="登录账号" />
        <input class="input" v-model="form.password" type="password" placeholder="登录密码" />
        <input class="input" v-model="form.email" placeholder="邮箱(选填)" />
        <input class="input" v-model="form.permissions" placeholder="权限模块(选填，逗号分隔)" />
        <view class="modal-btns">
          <button class="btn-cancel" @click="showForm = false">取消</button>
          <button class="btn-confirm" @click="doCreate">确认创建</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getSubAdmins, createSubAdmin, deleteSubAdmin } from "@/api/admin";

const subs = ref<any[]>([]);
const showForm = ref(false);
const form = ref({ display_name: "", username: "", password: "", email: "", permissions: "" });

onMounted(loadData);
async function loadData() { try { subs.value = await getSubAdmins(); } catch {} }

async function doCreate() {
  if (!form.value.display_name || !form.value.username || !form.value.password) {
    uni.showToast({ title: "请填写必填项", icon: "none" }); return;
  }
  try {
    await createSubAdmin(form.value);
    uni.showToast({ title: "创建成功", icon: "success" });
    showForm.value = false;
    form.value = { display_name: "", username: "", password: "", email: "", permissions: "" };
    loadData();
  } catch (e: any) { uni.showToast({ title: e.detail || "失败", icon: "none" }); }
}

async function remove(s: any) {
  const res = await uni.showModal({ title: "确认删除", content: `确定删除 ${s.display_name} 吗？` });
  if (!res.confirm) return;
  try {
    await deleteSubAdmin(s.id);
    uni.showToast({ title: "已删除", icon: "success" });
    loadData();
  } catch {}
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: bold; color: #303133; }
.add-btn { background: #409eff; color: #fff; font-size: 14px; padding: 6px 16px; border-radius: 6px; border: none; }
.empty { text-align: center; color: #909399; padding: 40px 0; }
.card { background: #fff; border-radius: 10px; padding: 14px; margin-bottom: 10px; }
.name { font-size: 16px; font-weight: bold; color: #303133; display: block; }
.info { font-size: 13px; color: #606266; display: block; margin-top: 4px; }
.actions { display: flex; gap: 16px; margin-top: 10px; justify-content: flex-end; }
.act { font-size: 13px; color: #409eff; }
.act.danger { color: #f56c6c; }
.modal-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { width: 85%; background: #fff; border-radius: 12px; padding: 20px; }
.modal-title { font-size: 18px; font-weight: bold; display: block; margin-bottom: 16px; }
.input { width: 100%; height: 40px; border: 1px solid #dcdfe6; border-radius: 6px; padding: 0 10px; margin-bottom: 10px; font-size: 14px; box-sizing: border-box; }
.modal-btns { display: flex; gap: 10px; justify-content: flex-end; margin-top: 10px; }
.btn-cancel { background: #f5f5f5; color: #606266; font-size: 14px; padding: 8px 20px; border-radius: 6px; border: none; }
.btn-confirm { background: #409eff; color: #fff; font-size: 14px; padding: 8px 20px; border-radius: 6px; border: none; }
</style>