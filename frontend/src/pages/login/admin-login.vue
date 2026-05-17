<template>
  <view class="container">
    <view class="login-card">
      <text class="title">管理后台登录</text>
      <text class="subtitle">咨询师 / 管理员入口</text>

      <view class="form-group">
        <text class="label">账号</text>
        <input class="input" v-model="username" placeholder="请输入登录账号" />
      </view>

      <view class="form-group">
        <text class="label">密码</text>
        <input class="input" v-model="password" type="password" placeholder="请输入密码" />
      </view>

      <button class="login-btn" @click="doAdminLogin" :loading="loading">登录</button>

      <view class="links">
        <text class="link" @click="goForgot">忘记密码？</text>
      </view>

      <view class="links">
        <text class="link" @click="goBack">← 返回用户端</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useUserStore } from "@/store/user";

const userStore = useUserStore();
const username = ref("");
const password = ref("");
const loading = ref(false);

async function doAdminLogin() {
  if (!username.value || !password.value) {
    uni.showToast({ title: "请输入账号和密码", icon: "none" });
    return;
  }
  loading.value = true;
  try {
    const res = await userStore.adminLogin({
      username: username.value,
      password: password.value,
    });
    if (res.must_change_password) {
      uni.redirectTo({ url: "/pages/login/change-password?force=1" });
    } else {
      uni.reLaunch({ url: "/pages/index/index" });
    }
  } catch (e: any) {
    uni.showToast({ title: e.detail || "登录失败，请检查账号密码", icon: "none" });
  } finally {
    loading.value = false;
  }
}

function goForgot() {
  uni.navigateTo({ url: "/pages/login/forgot-password" });
}

function goBack() {
  uni.navigateBack();
}
</script>

<style lang="scss" scoped>
.container {
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}
.login-card {
  width: 100%; max-width: 360px; background: #fff; border-radius: 16px;
  padding: 32px 24px; box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}
.title { font-size: 24px; font-weight: bold; color: #303133; display: block; text-align: center; }
.subtitle { font-size: 13px; color: #909399; display: block; text-align: center; margin-top: 6px; margin-bottom: 28px; }
.form-group { margin-bottom: 18px; }
.label { font-size: 14px; color: #606266; display: block; margin-bottom: 6px; }
.input {
  width: 100%; height: 44px; padding: 0 12px; border: 1px solid #dcdfe6;
  border-radius: 8px; font-size: 15px; box-sizing: border-box;
}
.login-btn {
  width: 100%; height: 46px; line-height: 46px; background: #667eea; color: #fff;
  border-radius: 8px; font-size: 16px; font-weight: 500; margin-top: 10px; border: none;
}
.login-btn:active { opacity: 0.85; }
.links { text-align: center; margin-top: 14px; }
.link { font-size: 14px; color: #409eff; }
</style>