<template>
  <view class="container">
    <view class="logo-area">
      <text class="logo-icon">🧠</text>
      <text class="app-name">AI 心理咨询助手</text>
      <text class="app-desc">在这里，每一次倾诉都被认真倾听</text>
    </view>

    <view class="login-area">
      <button class="wechat-btn" @click="doWechatLogin" :loading="loading">
        <text class="wechat-icon">�</text>
        <text>微信一键登录</text>
      </button>

      <view class="tips">
        <text>登录即表示同意</text>
        <text class="link" @click="showTerms">《服务协议》</text>
        <text>和</text>
        <text class="link" @click="showPrivacy">《隐私政策》</text>
      </view>

      <view class="admin-entry" @click="goAdminLogin">
        <text>我是咨询师/管理员 → 管理后台登录</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useUserStore } from "@/store/user";

const userStore = useUserStore();
const loading = ref(false);

function generateMockOpenid() {
  return "wx_h5_sim_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8);
}

async function doWechatLogin() {
  loading.value = true;
  try {
    await userStore.wechatLogin({
      openid: generateMockOpenid(),
      display_name: "微信用户" + Math.random().toString(36).slice(2, 6),
    });
    uni.reLaunch({ url: "/pages/index/index" });
  } catch (e: any) {
    uni.showToast({ title: e.detail || "登录失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

function goAdminLogin() {
  uni.navigateTo({ url: "/pages/login/admin-login" });
}

function showTerms() {
  uni.showToast({ title: "服务协议页（待开发）", icon: "none" });
}

function showPrivacy() {
  uni.showToast({ title: "隐私政策页（待开发）", icon: "none" });
}
</script>

<style lang="scss" scoped>
.container {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; min-height: 100vh; background: linear-gradient(135deg, #f5f7fa 0%, #e4efe9 100%);
  padding: 20px;
}
.logo-area { display: flex; flex-direction: column; align-items: center; margin-bottom: 50px; }
.logo-icon { font-size: 64px; margin-bottom: 16px; }
.app-name { font-size: 28px; font-weight: bold; color: #303133; margin-bottom: 8px; }
.app-desc { font-size: 14px; color: #909399; }

.login-area { width: 100%; max-width: 320px; }
.wechat-btn {
  width: 100%; height: 50px; display: flex; align-items: center;
  justify-content: center; background: #07c160; color: #fff;
  border-radius: 25px; font-size: 17px; font-weight: 500; border: none;
}
.wechat-btn:active { opacity: 0.8; }
.wechat-icon { margin-right: 8px; font-size: 20px; }
.tips { text-align: center; margin-top: 20px; font-size: 12px; color: #909399; }
.link { color: #409eff; }
.admin-entry { margin-top: 30px; text-align: center; }
.admin-entry text { font-size: 14px; color: #409eff; }
</style>