<template>
  <view class="container">
    <view class="card">
      <text class="title">忘记密码</text>
      <text class="subtitle">仅限咨询师/管理员账号，用户请使用微信登录</text>

      <view class="form-group">
        <text class="label">注册邮箱</text>
        <input class="input" v-model="email" placeholder="请输入注册时使用的邮箱" />
      </view>

      <button class="btn" @click="doForgot" :loading="loading">发送重置链接</button>
      <text class="link" @click="goBack">← 返回登录</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { forgotPassword } from "@/api/auth";

const email = ref("");
const loading = ref(false);

async function doForgot() {
  if (!email.value) {
    uni.showToast({ title: "请输入邮箱", icon: "none" });
    return;
  }
  loading.value = true;
  try {
    await forgotPassword({ email: email.value });
    uni.showModal({
      title: "发送成功",
      content: "如果该邮箱已注册，重置链接已发送。请在30分钟内完成重置。",
      showCancel: false,
      success: () => uni.navigateBack(),
    });
  } catch (e: any) {
    uni.showToast({ title: e.detail || "发送失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

function goBack() {
  uni.navigateBack();
}
</script>

<style lang="scss" scoped>
.container {
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh; background: #f5f5f5; padding: 20px;
}
.card { width: 100%; max-width: 360px; background: #fff; border-radius: 12px; padding: 28px 22px; }
.title { font-size: 22px; font-weight: bold; color: #303133; display: block; text-align: center; }
.subtitle { font-size: 12px; color: #909399; display: block; text-align: center; margin-top: 6px; margin-bottom: 24px; }
.form-group { margin-bottom: 18px; }
.label { font-size: 14px; color: #606266; display: block; margin-bottom: 6px; }
.input { width: 100%; height: 44px; padding: 0 12px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 15px; box-sizing: border-box; }
.btn { width: 100%; height: 44px; line-height: 44px; background: #409eff; color: #fff; border-radius: 8px; font-size: 16px; border: none; }
.link { font-size: 13px; color: #909399; text-align: center; display: block; margin-top: 14px; }
</style>