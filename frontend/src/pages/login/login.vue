<template>
  <view class="page">
    <view class="bg-decoration">
      <view class="circle c1"></view>
      <view class="circle c2"></view>
    </view>

    <!-- 品牌区 -->
    <view class="brand">
      <view class="brand-icon-wrap">
        <text class="brand-icon">🧠</text>
      </view>
      <text class="brand-name">AI 心理咨询助手</text>
      <text class="brand-desc">每一次倾诉，都被认真倾听</text>
    </view>

    <!-- 入口卡片 -->
    <view class="entry-card">
      <!-- 来访者入口 -->
      <view class="visitor-section">
        <view class="section-header">
          <text class="section-icon">👤</text>
          <text class="section-title">我是来访者</text>
          <text class="section-badge">免费倾诉</text>
        </view>
        <text class="section-desc">匿名与 AI 对话，获得即时情绪疏导</text>

        <button
          class="wechat-btn"
          @click="doWechatLogin"
          :loading="loading"
          :disabled="!agreed || loading"
        >
          <text class="wechat-icon">💬</text>
          <text>微信一键登录</text>
        </button>

        <view class="agreement">
          <label class="agreement-label" @click="agreed = !agreed">
            <view class="checkbox" :class="{ checked: agreed }">
              <text v-if="agreed" class="checkmark">✓</text>
            </view>
            <text class="agree-text">已阅读并同意</text>
            <text class="link" @click.stop="showTerms">《服务协议》</text>
            <text class="agree-text">和</text>
            <text class="link" @click.stop="showPrivacy">《隐私政策》</text>
          </label>
        </view>
      </view>

      <!-- 分割线 -->
      <view class="divider">
        <view class="divider-line"></view>
        <text class="divider-text">or</text>
        <view class="divider-line"></view>
      </view>

      <!-- 咨询师入口 -->
      <view class="counselor-section">
        <view class="section-header">
          <text class="section-icon">👩‍⚕️</text>
          <text class="section-title">我是咨询师</text>
          <text class="section-badge staff-badge">专业服务</text>
        </view>
        <text class="section-desc">注册咨询师账号，管理预约与对话记录</text>

        <button class="register-btn" @click="goRegister">
          <text class="register-icon">📝</text>
          <text class="register-text">注册咨询师账号</text>
          <text class="register-arrow">→</text>
        </button>

        <view class="login-hint">
          <text class="hint-text">已有账号？</text>
          <text class="hint-link" @click="goCounselorLogin">去登录</text>
        </view>
      </view>
    </view>

    <!-- 底部 -->
    <view class="footer">
      <text class="disclaimer">本 AI 助手不能替代专业心理咨询诊断</text>
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
$primary: #5b8c7e;
$primary-dark: #4a7568;
$bg: #f5f3ef;
$text-primary: #2c3e50;
$text-secondary: #7a8a8a;
$text-muted: #aab7b7;

.page {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(165deg, #f0ebe4 0%, #e4efe9 40%, #f5f3ef 100%);
  padding: 0 20px;
  overflow: hidden;
}

// 背景装饰
.bg-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.3;
}

.circle.c1 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, $primary 0%, transparent 70%);
  top: -80px; right: -60px;
  opacity: 0.15;
}

.circle.c2 {
  width: 200px; height: 200px;
  background: radial-gradient(circle, #c97b63 0%, transparent 70%);
  bottom: 60px; left: -40px;
  opacity: 0.12;
}

// 品牌区
.brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 44px 0 32px;
  position: relative;
  z-index: 1;
}

.brand-icon-wrap {
  width: 72px;
  height: 72px;
  border-radius: 22px;
  background: linear-gradient(135deg, #fff, #f8faf9);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
  box-shadow: 0 6px 20px rgba(91, 140, 126, 0.15);
}

.brand-icon { font-size: 36px; }

.brand-name {
  font-size: 24px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 6px;
  letter-spacing: 0.5px;
}

.brand-desc {
  font-size: 14px;
  color: $text-secondary;
  letter-spacing: 0.3px;
}

// 入口卡片
.entry-card {
  width: 100%;
  max-width: 380px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(91, 140, 126, 0.08);
  position: relative;
  z-index: 1;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.section-icon { font-size: 16px; }

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
}

.section-badge {
  font-size: 10px;
  color: #fff;
  background: $primary;
  padding: 1px 8px;
  border-radius: 8px;
  font-weight: 500;
  margin-left: auto;
}

.staff-badge {
  background: #c97b63;
}

.section-desc {
  font-size: 13px;
  color: $text-secondary;
  display: block;
  margin-bottom: 14px;
  line-height: 1.4;
}

// 来访者按钮
.visitor-section { padding: 4px 0; }

.wechat-btn {
  width: 100%;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, $primary, $primary-dark);
  color: #fff;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  box-shadow: 0 4px 14px rgba(91, 140, 126, 0.25);
  transition: all 0.2s;
}

.wechat-btn:active { transform: scale(0.97); opacity: 0.9; }
.wechat-btn[disabled] { opacity: 0.5; box-shadow: none; }
.wechat-icon { margin-right: 8px; font-size: 18px; }

// 协议
.agreement { margin-top: 12px; }

.agreement-label {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 2px;
  font-size: 12px;
  color: $text-muted;
}

.checkbox {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1.5px solid #d0d5d5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 4px;
  flex-shrink: 0;
  transition: all 0.2s;
}

.checkbox.checked { background: $primary; border-color: $primary; }
.checkmark { color: #fff; font-size: 10px; font-weight: bold; }
.agree-text { font-size: 12px; color: $text-muted; }
.link { color: $primary; font-size: 12px; }

// 分割线
.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 20px 0;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(to right, transparent, #dde5e2, transparent);
}

.divider-text { font-size: 12px; color: $text-muted; font-weight: 500; }

// 咨询师入口
.counselor-section { padding: 4px 0; }

.register-btn {
  width: 100%;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  color: $text-primary;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  border: 1.5px solid #e0e8e5;
  transition: all 0.2s;
}

.register-btn:active {
  background: #f5f8f7;
  border-color: #c97b63;
  transform: scale(0.98);
}

.register-icon { margin-right: 8px; font-size: 16px; }
.register-text { flex: 1; text-align: center; }
.register-arrow { font-size: 16px; color: $text-muted; }

.login-hint {
  text-align: center;
  margin-top: 10px;
}

.hint-text { font-size: 13px; color: $text-muted; }
.hint-link { font-size: 13px; color: $primary; margin-left: 4px; }

// 底部
.footer { padding: 24px 0 32px; position: relative; z-index: 1; }
.disclaimer { font-size: 11px; color: $text-muted; text-align: center; }
</style>
