<template>
  <view class="page">
    <view class="bg-decoration">
      <view class="blob b1"></view>
      <view class="blob b2"></view>
    </view>

    <view class="login-card">
      <!-- 品牌标识 -->
      <view class="card-header">
        <view class="mini-logo">
          <text class="mini-logo-text">🧠</text>
        </view>
        <text class="card-title">咨询师通道</text>
        <text class="card-subtitle">登录或注册咨询师账号</text>
      </view>

      <!-- 选项卡 -->
      <view class="tabs">
        <view
          class="tab"
          :class="{ active: currentTab === 'login' }"
          @click="currentTab = 'login'"
        >
          <text class="tab-icon">🔐</text>
          <text class="tab-text">登录</text>
        </view>
        <view
          class="tab"
          :class="{ active: currentTab === 'register' }"
          @click="currentTab = 'register'"
        >
          <text class="tab-icon">📝</text>
          <text class="tab-text">注册</text>
        </view>
      </view>

      <!-- 登录表单 -->
      <view v-if="currentTab === 'login'" class="form-container">
        <view class="form-group">
          <text class="label">账号</text>
          <view class="input-wrap">
            <text class="input-icon">👤</text>
            <input class="input" v-model="username" placeholder="请输入登录账号" />
          </view>
        </view>

        <view class="form-group">
          <text class="label">密码</text>
          <view class="input-wrap">
            <text class="input-icon">🔑</text>
            <input class="input" v-model="password" type="password" placeholder="请输入密码" />
          </view>
        </view>

        <button class="primary-btn" @click="doLogin" :loading="loading">
          登录
        </button>

        <view class="form-links">
          <text class="link" @click="goForgot">忘记密码？</text>
        </view>
      </view>

      <!-- 注册表单 -->
      <view v-if="currentTab === 'register'" class="form-container">
        <view class="register-tip">
          <text class="register-tip-icon">💡</text>
          <text class="register-tip-text">注册后可直接登录使用，超级管理员审核后正式生效</text>
        </view>

        <view class="form-group">
          <text class="label">姓名</text>
          <view class="input-wrap">
            <text class="input-icon">📛</text>
            <input class="input" v-model="regName" placeholder="请输入您的姓名" />
          </view>
        </view>

        <view class="form-group">
          <text class="label">登录账号</text>
          <view class="input-wrap">
            <text class="input-icon">👤</text>
            <input class="input" v-model="regUsername" placeholder="字母或数字，至少3位" />
          </view>
        </view>

        <view class="form-group">
          <text class="label">密码</text>
          <view class="input-wrap">
            <text class="input-icon">🔑</text>
            <input class="input" v-model="regPassword" type="password" placeholder="至少6位" />
          </view>
        </view>

        <view class="form-group">
          <text class="label">专业领域 <text class="optional">（选填）</text></text>
          <view class="input-wrap">
            <text class="input-icon">🎯</text>
            <input class="input" v-model="regSpecialties" placeholder="如：情绪管理、人际关系、学业压力" />
          </view>
        </view>

        <view class="form-group">
          <text class="label">个人简介 <text class="optional">（选填）</text></text>
          <view class="input-wrap textarea-wrap">
            <textarea class="textarea" v-model="regBio" placeholder="简单介绍您的专业背景和从业经历" maxlength="200" />
          </view>
        </view>

        <button class="primary-btn register-btn" @click="doRegister" :loading="regLoading">
          注册
        </button>

        <view class="form-links">
          <text class="link-gray">已有账号？</text>
          <text class="link" @click="currentTab = 'login'">去登录</text>
        </view>
      </view>

      <!-- 返回 -->
      <view class="back-row">
        <text class="back-link" @click="goBack">← 返回首页</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { useUserStore } from "@/store/user";
import { request } from "@/utils/request";

const userStore = useUserStore();

const currentTab = ref("login");

// 登录
const username = ref("");
const password = ref("");
const loading = ref(false);

// 注册
const regName = ref("");
const regUsername = ref("");
const regPassword = ref("");
const regSpecialties = ref("");
const regBio = ref("");
const regLoading = ref(false);

onLoad((options: any) => {
  if (options?.tab === "register") {
    currentTab.value = "register";
  }
});

async function doLogin() {
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

async function doRegister() {
  if (!regName.value) {
    uni.showToast({ title: "请输入姓名", icon: "none" });
    return;
  }
  if (!regUsername.value || regUsername.value.length < 3) {
    uni.showToast({ title: "账号至少3位字符", icon: "none" });
    return;
  }
  if (!regPassword.value || regPassword.value.length < 6) {
    uni.showToast({ title: "密码至少6位", icon: "none" });
    return;
  }
  regLoading.value = true;
  try {
    await request("/api/auth/counselor-register", {
      method: "POST",
      data: {
        display_name: regName.value,
        username: regUsername.value,
        password: regPassword.value,
        specialties: regSpecialties.value || undefined,
        bio: regBio.value || undefined,
      },
    });
    uni.showToast({ title: "注册成功，请等待管理员审核", icon: "success" });
    currentTab.value = "login";
    username.value = regUsername.value;
  } catch (e: any) {
    uni.showToast({ title: e.detail || "注册失败", icon: "none" });
  } finally {
    regLoading.value = false;
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
$primary: #5b8c7e;
$primary-dark: #4a7568;
$text-primary: #2c3e50;
$text-secondary: #7a8a8a;
$text-muted: #aab7b7;

.page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(145deg, #f0ebe4 0%, #e4efe9 50%, #f5f3ef 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.bg-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
}

.blob.b1 {
  width: 280px; height: 280px;
  background: rgba(91, 140, 126, 0.12);
  top: -60px; right: -40px;
}

.blob.b2 {
  width: 220px; height: 220px;
  background: rgba(201, 123, 99, 0.1);
  bottom: -40px; left: -60px;
}

// 卡片
.login-card {
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 28px;
  padding: 32px 28px;
  box-shadow: 0 12px 40px rgba(91, 140, 126, 0.1);
  position: relative;
  z-index: 1;
}

.card-header {
  text-align: center;
  margin-bottom: 24px;
}

.mini-logo {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: linear-gradient(135deg, #fff, #f5f8f7);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  box-shadow: 0 4px 12px rgba(91, 140, 126, 0.1);
}

.mini-logo-text { font-size: 24px; }

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: $text-primary;
  display: block;
  letter-spacing: 0.3px;
}

.card-subtitle {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-top: 4px;
}

// 选项卡
.tabs {
  display: flex;
  background: #f0f4f2;
  border-radius: 14px;
  padding: 4px;
  margin-bottom: 24px;
  gap: 4px;
}

.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 0;
  border-radius: 11px;
  transition: all 0.25s ease;
}

.tab.active {
  background: #fff;
  box-shadow: 0 2px 8px rgba(91, 140, 126, 0.08);
}

.tab-icon { font-size: 14px; }
.tab-text { font-size: 14px; font-weight: 500; color: $text-muted; }
.tab.active .tab-text { color: $text-primary; font-weight: 600; }

// 注册提示
.register-tip {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: #f0f7f4;
  border-radius: 12px;
  margin-bottom: 16px;
}

.register-tip-icon { font-size: 14px; flex-shrink: 0; margin-top: 1px; }
.register-tip-text { font-size: 12px; color: $text-secondary; line-height: 1.5; }

// 表单
.form-group { margin-bottom: 16px; }

.label {
  font-size: 13px;
  font-weight: 500;
  color: $text-primary;
  display: block;
  margin-bottom: 6px;
}

.optional { font-size: 12px; color: $text-muted; font-weight: 400; }

.input-wrap {
  display: flex;
  align-items: center;
  background: #f5f8f7;
  border: 1.5px solid #e0e8e5;
  border-radius: 12px;
  padding: 0 14px;
  transition: border-color 0.2s;
}

.input-wrap:focus-within {
  border-color: $primary;
  background: #fff;
}

.input-icon { font-size: 14px; margin-right: 10px; flex-shrink: 0; }

.input {
  flex: 1;
  height: 46px;
  font-size: 15px;
  color: $text-primary;
  background: transparent;
  border: none;
  outline: none;
}

.input::placeholder { color: #c5cecb; }

.textarea-wrap { align-items: flex-start; padding: 12px 14px; }

.textarea {
  width: 100%;
  min-height: 72px;
  font-size: 14px;
  color: $text-primary;
  background: transparent;
  border: none;
  outline: none;
  line-height: 1.5;
}

.textarea::placeholder { color: #c5cecb; }

.primary-btn {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, $primary, $primary-dark);
  color: #fff;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  margin-top: 4px;
  box-shadow: 0 4px 14px rgba(91, 140, 126, 0.2);
  transition: all 0.2s;
}

.primary-btn:active { transform: scale(0.97); opacity: 0.9; }
.primary-btn[disabled] { opacity: 0.5; box-shadow: none; }

.register-btn {
  background: linear-gradient(135deg, #c97b63, #b86a52);
  box-shadow: 0 4px 14px rgba(201, 123, 99, 0.25);
}

.form-links { text-align: center; margin-top: 14px; }
.link { font-size: 14px; color: $primary; }
.link-gray { font-size: 14px; color: $text-muted; }

.back-row {
  text-align: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f0f4f2;
}

.back-link { font-size: 13px; color: $text-muted; }
</style>
