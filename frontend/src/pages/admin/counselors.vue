<template>
  <view class="container">
    <view class="header">
      <text class="page-title">咨询师管理</text>
      <button class="add-btn" @click="showForm = true">+ 添加</button>
    </view>

    <view v-if="counselors.length === 0" class="empty">暂无咨询师</view>

    <view v-for="c in counselors" :key="c.id" class="card">
      <view class="card-row">
        <text class="name">{{ c.display_name }}</text>
        <text class="status" :class="c.status">{{ c.status === 'active' ? '正常' : c.status === 'disabled' ? '已禁用' : '已删除' }}</text>
      </view>
      <text class="info">账号: {{ c.username }}</text>
      <text v-if="c.specialties" class="info">擅长: {{ c.specialties }}</text>
      <view class="actions">
        <text class="act" @click="resetPwd(c)">重置密码</text>
        <text v-if="c.status === 'active'" class="act warn" @click="toggleStatus(c, 'disable')">禁用</text>
        <text v-if="c.status === 'disabled'" class="act ok" @click="toggleStatus(c, 'enable')">启用</text>
        <text v-if="c.status !== 'deleted'" class="act danger" @click="remove(c)">删除</text>
      </view>
    </view>

    <view v-if="showForm" class="modal-mask" @click="showForm = false">
      <view class="modal" @click.stop>
        <text class="modal-title">添加咨询师</text>
        <input class="input" v-model="form.display_name" placeholder="姓名" />
        <input class="input" v-model="form.username" placeholder="登录账号" />
        <input class="input" v-model="form.password" type="password" placeholder="登录密码(至少6位)" />
        <input class="input" v-model="form.email" placeholder="邮箱(选填)" />
        <input class="input" v-model="form.specialties" placeholder="擅长领域(选填)" />
        <textarea class="input textarea" v-model="form.bio" placeholder="简介(选填)" />
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
import { getCounselors, createCounselor, resetCounselorPassword, disableCounselor, enableCounselor, deleteCounselor } from "@/api/admin";

const counselors = ref<any[]>([]);
const showForm = ref(false);
const form = ref({ display_name: "", username: "", password: "", email: "", specialties: "", bio: "" });

onMounted(loadData);

async function loadData() {
  try { counselors.value = await getCounselors(); } catch {}
}

async function doCreate() {
  if (!form.value.display_name || !form.value.username || !form.value.password) {
    uni.showToast({ title: "请填写必填项", icon: "none" }); return;
  }
  try {
    await createCounselor(form.value);
    uni.showToast({ title: "创建成功", icon: "success" });
    showForm.value = false;
    form.value = { display_name: "", username: "", password: "", email: "", specialties: "", bio: "" };
    loadData();
  } catch (e: any) { uni.showToast({ title: e.detail || "失败", icon: "none" }); }
}

async function resetPwd(c: any) {
  const res = await uni.showModal({ title: "重置密码", content: `确定重置 ${c.display_name} 的密码吗？` });
  if (!res.confirm) return;
  try {
    await resetCounselorPassword(c.id, "reset123456");
    uni.showToast({ title: "已重置为 reset123456", icon: "success" });
  } catch {}
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

async function remove(c: any) {
  const { confirm } = await uni.showModal({ title: "确认删除", content: `确定删除 ${c.display_name} 吗？数据将保留。` });
  if (!confirm) return;
  try {
    await deleteCounselor(c.id);
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
.card-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.name { font-size: 16px; font-weight: bold; color: #303133; }
.status { font-size: 12px; padding: 2px 8px; border-radius: 4px; }
.status.active { color: #67c23a; background: #f0f9eb; }
.status.disabled { color: #e6a23c; background: #fdf6ec; }
.status.deleted { color: #f56c6c; background: #fef0f0; }
.info { font-size: 13px; color: #606266; display: block; margin-top: 2px; }
.actions { display: flex; gap: 16px; margin-top: 10px; justify-content: flex-end; }
.act { font-size: 13px; color: #409eff; }
.act.warn { color: #e6a23c; }
.act.ok { color: #67c23a; }
.act.danger { color: #f56c6c; }

.modal-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { width: 85%; background: #fff; border-radius: 12px; padding: 20px; }
.modal-title { font-size: 18px; font-weight: bold; color: #303133; display: block; margin-bottom: 16px; }
.input { width: 100%; height: 40px; border: 1px solid #dcdfe6; border-radius: 6px; padding: 0 10px; margin-bottom: 10px; font-size: 14px; box-sizing: border-box; }
.textarea { height: 70px; padding: 8px 10px; }
.modal-btns { display: flex; gap: 10px; justify-content: flex-end; margin-top: 10px; }
.btn-cancel { background: #f5f5f5; color: #606266; font-size: 14px; padding: 8px 20px; border-radius: 6px; border: none; }
.btn-confirm { background: #409eff; color: #fff; font-size: 14px; padding: 8px 20px; border-radius: 6px; border: none; }
</style>