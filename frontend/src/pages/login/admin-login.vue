<template>
  <view class="page">
    <view class="bg-ornament">
      <view class="bg-blur bl-1"></view>
      <view class="bg-blur bl-2"></view>
    </view>

    <view class="login-card">
      <!-- 品牌 -->
      <view class="card-top">
        <view class="card-logo">
          <text class="card-logo-sigil">&#x2737;</text>
        </view>
        <text class="card-title">咨询师通道</text>
        <text class="card-subtitle">登录或注册咨询师账号</text>
      </view>

      <!-- 选项卡 -->
      <view class="tabs">
        <view
          class="tab"
          :class="{ 'tab-active': currentTab === 'login' }"
          @click="currentTab = 'login'"
        >
          <text class="tab-label">登录</text>
        </view>
        <view
          class="tab"
          :class="{ 'tab-active': currentTab === 'register' }"
          @click="currentTab = 'register'"
        >
          <text class="tab-label">注册</text>
        </view>
      </view>

      <!-- 登录 -->
      <view v-if="currentTab === 'login'" class="form-box">
        <view class="field">
          <text class="field-label">账号</text>
          <view class="field-wrap">
            <text class="field-symbol">&#x263A;</text>
            <input class="field-input" v-model="username" placeholder="请输入登录账号" />
          </view>
        </view>

        <view class="field">
          <text class="field-label">密码</text>
          <view class="field-wrap">
            <text class="field-symbol">&#x26BF;</text>
            <input class="field-input" v-model="password" type="password" placeholder="请输入密码" />
          </view>
        </view>

        <button class="btn-submit" @click="doLogin" :loading="loading">
          登录
        </button>

        <view class="form-foot">
          <text class="foot-link" @click="goForgot">忘记密码？</text>
        </view>
      </view>

      <!-- 注册 -->
      <view v-if="currentTab === 'register'" class="form-box">
        <view class="reg-notice">
          <text class="notice-dot">&bull;</text>
          <text class="notice-text">注册后可直接登录，管理员审核后正式生效</text>
        </view>

        <view class="field">
          <text class="field-label">姓名</text>
          <view class="field-wrap">
            <text class="field-symbol">&#x263A;</text>
            <input class="field-input" v-model="regName" placeholder="请输入您的姓名" />
          </view>
        </view>

        <view class="field">
          <text class="field-label">登录账号</text>
          <view class="field-wrap">
            <text class="field-symbol">&#x263D;</text>
            <input class="field-input" v-model="regUsername" placeholder="字母或数字，至少3位" />
          </view>
        </view>

        <view class="field">
          <text class="field-label">密码</text>
          <view class="field-wrap">
            <text class="field-symbol">&#x26BF;</text>
            <input class="field-input" v-model="regPassword" type="password" placeholder="至少6位" />
          </view>
        </view>

        <view class="field">
          <text class="field-label">专业领域 <text class="field-optional">（选填）</text></text>
          <view class="field-wrap">
            <text class="field-symbol">&#x2702;</text>
            <input class="field-input" v-model="regSpecialties" placeholder="如：情绪管理、人际关系" />
          </view>
        </view>

        <view class="field">
          <text class="field-label">个人简介 <text class="field-optional">（选填）</text></text>
          <view class="field-wrap field-textarea">
            <textarea class="ta-input" v-model="regBio" placeholder="简单介绍您的专业背景" maxlength="200" />
          </view>
        </view>

        <button class="btn-submit btn-reg" @click="doRegister" :loading="regLoading">
          注册
        </button>

        <view class="form-foot">
          <text class="foot-muted">已有账号？</text>
          <text class="foot-link" @click="currentTab = 'login'">去登录</text>
        </view>
      </view>

      <!-- 返回 -->
      <view class="card-back">
        <text class="back-link" @click="goBack">&larr; 返回首页</text>
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

const username = ref("");
const password = ref("");
const loading = ref(false);

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
// ====================================================
//  Warm Amber - 咨询师登录
// ====================================================
$primary:       #D4956A;
$primary-dark:  #B87A52;
$primary-light: #F0DCC8;
$primary-pale:  #F8EDE2;

$text-primary:  #3D322A;
$text-secondary:#8A8275;
$text-muted:    #B5A99A;

$border-soft:   #E8E0D0;
$card-bg:       rgba(255, 255, 255, 0.92);
$bg-from:       #FDF8F4;
$bg-to:         #F8EDE2;

$radius-card:   28px;
$radius-pill:   30px;
$font-stack:    -apple-system, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;

.page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(145deg, $bg-from 0%, $bg-to 50%, #F0E3D0 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
  font-family: $font-stack;
}

.bg-ornament {
  position: fixed;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-blur {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
}

.bl-1 {
  width: 280px;
  height: 280px;
  background: rgba($primary, 0.1);
  top: -60px;
  right: -40px;
}

.bl-2 {
  width: 220px;
  height: 220px;
  background: rgba($primary-dark, 0.08);
  bottom: -40px;
  left: -60px;
}

//  卡片
.login-card {
  width: 100%;
  max-width: 400px;
  background: $card-bg;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: $radius-card;
  padding: 32px 28px;
  box-shadow: 0 12px 40px rgba(61, 50, 42, 0.08);
  position: relative;
  z-index: 1;
}

.card-top {
  text-align: center;
  margin-bottom: 24px;
}

.card-logo {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: linear-gradient(135deg, $primary, $primary-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  box-shadow: 0 4px 12px rgba($primary-dark, 0.15);
}

.card-logo-sigil {
  font-size: 22px;
  color: #fff;
  font-weight: 400;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: $text-primary;
  display: block;
  letter-spacing: 0.04em;
}

.card-subtitle {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-top: 4px;
}

//  选项卡
.tabs {
  display: flex;
  background: $primary-pale;
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
  padding: 10px 0;
  border-radius: 11px;
  transition: all 0.25s ease;
}

.tab-active {
  background: #fff;
  box-shadow: 0 2px 8px rgba(61, 50, 42, 0.05);
}

.tab-label {
  font-size: 14px;
  font-weight: 500;
  color: $text-muted;
}

.tab-active .tab-label {
  color: $text-primary;
  font-weight: 600;
}

//  表单区域
.form-box {
}

//  注册提示
.reg-notice {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 14px;
  background: $primary-pale;
  border-radius: 12px;
  margin-bottom: 16px;
}

.notice-dot {
  font-size: 14px;
  color: $primary;
  flex-shrink: 0;
  margin-top: 1px;
}

.notice-text {
  font-size: 12px;
  color: $text-secondary;
  line-height: 1.5;
}

//  字段
.field {
  margin-bottom: 16px;
}

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: $text-primary;
  display: block;
  margin-bottom: 6px;
}

.field-optional {
  font-size: 12px;
  color: $text-muted;
  font-weight: 400;
}

.field-wrap {
  display: flex;
  align-items: center;
  background: $bg-from;
  border: 1.5px solid $border-soft;
  border-radius: 12px;
  padding: 0 14px;
  transition: border-color 0.2s;
}

.field-wrap:focus-within {
  border-color: $primary;
  background: #fff;
}

.field-symbol {
  font-size: 14px;
  color: $text-muted;
  margin-right: 10px;
  flex-shrink: 0;
}

.field-input {
  flex: 1;
  height: 46px;
  font-size: 15px;
  color: $text-primary;
  background: transparent;
  border: none;
  outline: none;
}

.field-input::placeholder {
  color: $text-muted;
}

.field-textarea {
  align-items: flex-start;
  padding: 12px 14px;
}

.ta-input {
  width: 100%;
  min-height: 72px;
  font-size: 14px;
  color: $text-primary;
  background: transparent;
  border: none;
  outline: none;
  line-height: 1.5;
}

.ta-input::placeholder {
  color: $text-muted;
}

//  按钮
.btn-submit {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, $primary, $primary-dark);
  color: #fff;
  border-radius: $radius-pill;
  font-size: 16px;
  font-weight: 600;
  border: none;
  margin-top: 4px;
  box-shadow: 0 4px 14px rgba($primary-dark, 0.2);
  transition: all 0.2s;
  letter-spacing: 0.03em;
}

.btn-submit:active {
  transform: scale(0.97);
  opacity: 0.9;
}

.btn-submit[disabled] {
  opacity: 0.5;
  box-shadow: none;
}

.btn-reg {
  background: linear-gradient(135deg, $primary-dark, #906055);
}

//  底部链接
.form-foot {
  text-align: center;
  margin-top: 14px;
}

.foot-link {
  font-size: 14px;
  color: $primary;
}

.foot-muted {
  font-size: 14px;
  color: $text-muted;
}

//  返回
.card-back {
  text-align: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid $border-soft;
}

.back-link {
  font-size: 13px;
  color: $text-muted;
}
</style>
