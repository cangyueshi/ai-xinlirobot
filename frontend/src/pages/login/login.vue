<template>
  <view class="page">
    <view class="bg-ornament">
      <view class="orn-circle oc-1"></view>
      <view class="orn-circle oc-2"></view>
      <view class="orn-blob"></view>
    </view>

    <!-- 品牌区 -->
    <view class="brand-zone">
      <view class="brand-mark">
        <view class="brand-icon">
          <text class="brand-icon-sigil">&hearts;</text>
        </view>
        <view class="brand-ring"></view>
      </view>
      <text class="brand-title">有聊心理</text>
      <text class="brand-tagline">有温度的 AI 心理陪伴</text>
    </view>

    <!-- 入口卡片 -->
    <view class="entry-card">
      <!-- 来访者 -->
      <view class="entry-block">
        <view class="entry-block-head">
          <text class="entry-block-title">我是来访者</text>
          <text class="entry-block-badge">免费倾诉</text>
        </view>
        <text class="entry-block-desc">与 AI 匿名对话，获得即时情绪疏导</text>

        <button
          class="btn-primary"
          @click="doWechatLogin"
          :loading="loading"
          :disabled="!agreed || loading"
        >
          <text class="btn-primary-icon">&#x2763;</text>
          <text>微信一键登录</text>
        </button>

        <view class="agreement-bar">
          <label class="agreement-label" @click="agreed = !agreed">
            <view class="ck-box" :class="{ 'ck-checked': agreed }">
              <text v-if="agreed" class="ck-mark">&#x2713;</text>
            </view>
            <text class="ck-text">已阅读并同意</text>
            <text class="ck-link" @click.stop="showTerms">《服务协议》</text>
            <text class="ck-text">和</text>
            <text class="ck-link" @click.stop="showPrivacy">《隐私政策》</text>
          </label>
        </view>
      </view>

      <!-- 分割 -->
      <view class="divider-rule">
        <view class="divider-line"></view>
        <text class="divider-label">or</text>
        <view class="divider-line"></view>
      </view>

      <!-- 咨询师 -->
      <view class="entry-block">
        <view class="entry-block-head">
          <text class="entry-block-title">我是咨询师</text>
          <text class="entry-block-badge badge-counselor">专业服务</text>
        </view>
        <text class="entry-block-desc">注册咨询师账号，管理预约与对话记录</text>

        <button class="btn-outline" @click="goRegister">
          <text class="btn-outline-label">注册咨询师账号</text>
          <text class="btn-outline-arrow">&rarr;</text>
        </button>

        <view class="switch-prompt">
          <text class="switch-text">已有账号？</text>
          <text class="switch-link" @click="goCounselorLogin">去登录</text>
        </view>
      </view>
    </view>

    <view class="footer-note">
      <text class="footer-disclaimer">AI 不能替代专业心理咨询诊断</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useUserStore } from "@/store/user";

const userStore = useUserStore();
const loading = ref(false);
const agreed = ref(false);

function generateMockOpenid() {
  return "wx_h5_sim_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8);
}

async function doWechatLogin() {
  if (!agreed.value) {
    uni.showToast({ title: "请先阅读并同意服务协议和隐私政策", icon: "none" });
    return;
  }
  loading.value = true;
  try {
    // #ifdef MP-WEIXIN
    const loginRes = await new Promise<any>((resolve, reject) => {
      uni.login({ provider: "weixin", success: (res) => resolve(res), fail: (err) => reject(err) });
    });
    const mpRes = await uni.request({
      url: `http://localhost:8000/api/auth/mp-login`,
      method: "POST",
      data: { code: loginRes.code },
    });
    const data = mpRes.data as any;
    if (!data.openid) throw new Error("微信登录失败");
    await userStore.wechatLogin({ openid: data.openid, display_name: data.display_name || "微信用户" });
    // #endif

    // #ifdef H5
    await userStore.wechatLogin({
      openid: generateMockOpenid(),
      display_name: "用户" + Math.random().toString(36).slice(2, 6),
    });
    // #endif

    uni.reLaunch({ url: "/pages/index/index" });
  } catch (e: any) {
    uni.showToast({ title: e?.errMsg || "登录失败，请重试", icon: "none" });
  } finally {
    loading.value = false;
  }
}

function goRegister() {
  uni.navigateTo({ url: "/pages/login/admin-login?tab=register" });
}

function goCounselorLogin() {
  uni.navigateTo({ url: "/pages/login/admin-login" });
}

function showTerms() {
  uni.navigateTo({ url: "/pages/login/terms" });
}

function showPrivacy() {
  uni.navigateTo({ url: "/pages/login/privacy" });
}
</script>

<style lang="scss" scoped>
// ====================================================
//  Warm Therapy - 登录页
// ====================================================
$primary:       #D4956A;
$primary-dark:  #B87A52;
$primary-pale:  #F8EDE2;
$primary-light: #F0DCC8;

$bg-gradient-1: #FDF8F4;
$bg-gradient-2: #F8EDE2;
$bg-gradient-3: #F0E3D0;

$text-primary:  #3D322A;
$text-secondary:#8A8275;
$text-muted:    #B5A99A;

$card-bg:       rgba(255, 255, 255, 0.88);
$border-light:  #E8E0D0;
$shadow-card:   0 8px 32px rgba(61, 50, 42, 0.07);

$radius-card:   24px;
$radius-pill:   30px;
$font-stack:    -apple-system, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;

.page {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(160deg, $bg-gradient-1 0%, $bg-gradient-2 35%, $bg-gradient-3 100%);
  padding: 0 24px;
  overflow: hidden;
  font-family: $font-stack;
}

//  背景装饰
.bg-ornament {
  position: fixed;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.orn-circle {
  position: absolute;
  border-radius: 50%;
}

.oc-1 {
  width: 320px;
  height: 320px;
  background: radial-gradient(circle, rgba($primary, 0.12), transparent 70%);
  top: -100px;
  right: -80px;
}

.oc-2 {
  width: 220px;
  height: 220px;
  background: radial-gradient(circle, rgba($primary-dark, 0.08), transparent 70%);
  bottom: 80px;
  left: -60px;
}

.orn-blob {
  position: absolute;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(#F0DCC8, 0.3), transparent 60%);
  top: 20%;
  left: -10%;
}

//  品牌区
.brand-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 0 28px;
  position: relative;
  z-index: 1;
}

.brand-mark {
  position: relative;
  margin-bottom: 18px;
}

.brand-icon {
  width: 68px;
  height: 68px;
  border-radius: 20px;
  background: linear-gradient(135deg, $primary, $primary-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
  box-shadow: 0 6px 20px rgba($primary-dark, 0.2);
}

.brand-icon-sigil {
  font-size: 28px;
  color: #fff;
  font-weight: 400;
}

.brand-ring {
  position: absolute;
  top: -4px;
  left: -4px;
  width: 76px;
  height: 76px;
  border-radius: 24px;
  border: 1.5px solid rgba($primary, 0.15);
}

.brand-title {
  font-size: 26px;
  font-weight: 700;
  color: $text-primary;
  letter-spacing: 0.08em;
  margin-bottom: 6px;
}

.brand-tagline {
  font-size: 14px;
  color: $text-secondary;
  letter-spacing: 0.04em;
}

//  入口卡片
.entry-card {
  width: 100%;
  max-width: 380px;
  background: $card-bg;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: $radius-card;
  padding: 28px 24px;
  box-shadow: $shadow-card;
  position: relative;
  z-index: 1;
}

.entry-block {
  padding: 2px 0;
}

.entry-block-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.entry-block-title {
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
  letter-spacing: 0.01em;
}

.entry-block-badge {
  font-size: 10px;
  color: #fff;
  background: $primary;
  padding: 2px 10px;
  border-radius: 8px;
  font-weight: 500;
  margin-left: auto;
  letter-spacing: 0.02em;
}

.badge-counselor {
  background: $primary-dark;
}

.entry-block-desc {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-bottom: 14px;
  line-height: 1.4;
}

//  主按钮
.btn-primary {
  width: 100%;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, $primary, $primary-dark);
  color: #fff;
  border-radius: $radius-pill;
  font-size: 16px;
  font-weight: 600;
  border: none;
  box-shadow: 0 4px 14px rgba($primary-dark, 0.25);
  transition: all 0.2s;
  letter-spacing: 0.02em;
}

.btn-primary:active {
  transform: scale(0.97);
  opacity: 0.9;
}

.btn-primary[disabled] {
  opacity: 0.5;
  box-shadow: none;
}

.btn-primary-icon {
  font-size: 16px;
}

//  协议
.agreement-bar {
  margin-top: 14px;
}

.agreement-label {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 2px;
  font-size: 12px;
  color: $text-muted;
}

.ck-box {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1.5px solid $border-light;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 4px;
  flex-shrink: 0;
  transition: all 0.2s;
}

.ck-checked {
  background: $primary;
  border-color: $primary;
}

.ck-mark {
  color: #fff;
  font-size: 10px;
  font-weight: bold;
}

.ck-text {
  font-size: 12px;
  color: $text-muted;
}

.ck-link {
  color: $primary;
  font-size: 12px;
}

//  分割线
.divider-rule {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 20px 0;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(to right, transparent, $border-light, transparent);
}

.divider-label {
  font-size: 12px;
  color: $text-muted;
  font-weight: 500;
}

//  轮廓按钮
.btn-outline {
  width: 100%;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: $text-primary;
  border-radius: $radius-pill;
  font-size: 15px;
  font-weight: 600;
  border: 1.5px solid $border-light;
  transition: all 0.2s;
}

.btn-outline:active {
  background: $primary-pale;
  border-color: $primary-light;
  transform: scale(0.98);
}

.btn-outline-label {
  flex: 1;
  text-align: center;
}

.btn-outline-arrow {
  font-size: 16px;
  color: $text-muted;
  padding-right: 4px;
}

.switch-prompt {
  text-align: center;
  margin-top: 12px;
}

.switch-text {
  font-size: 13px;
  color: $text-muted;
}

.switch-link {
  font-size: 13px;
  color: $primary;
  margin-left: 4px;
}

//  底部
.footer-note {
  padding: 28px 0 32px;
  position: relative;
  z-index: 1;
}

.footer-disclaimer {
  font-size: 11px;
  color: $text-muted;
  text-align: center;
  letter-spacing: 0.02em;
}
</style>
