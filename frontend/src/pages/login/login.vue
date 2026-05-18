<template>
  <view class="container">
    <view class="logo-area">
      <text class="logo-icon">🧠</text>
      <text class="app-name">AI 心理咨询助手</text>
      <text class="app-desc">在这里，每一次倾诉都被认真倾听</text>
    </view>

    <view class="login-area">
      <button class="wechat-btn" @click="doWechatLogin" :loading="loading" :disabled="!agreed || loading">
        <text class="wechat-icon">�</text>
        <text>微信一键登录</text>
      </button>

      <view class="agreement">
        <label class="agreement-label" @click="agreed = !agreed">
          <text :class="['checkbox', { checked: agreed }]">{{ agreed ? '☑' : '☐' }}</text>
          <text>我已阅读并同意</text>
          <text class="link" @click.stop="showTerms">《服务协议》</text>
          <text>和</text>
          <text class="link" @click.stop="showPrivacy">《隐私政策》</text>
        </label>
        <text class="disclaimer">本 AI 助手不能替代专业心理咨询诊断</text>
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
    // 微信小程序模式：通过 wx.login() 获取 code，由后端换 openid
    const loginRes = await new Promise<WechatMiniprogram.LoginSuccessCallbackResult>((resolve, reject) => {
      uni.login({
        provider: "weixin",
        success: (res) => resolve(res),
        fail: (err) => reject(err),
      });
    });
    const mpRes = await uni.request({
      url: `http://localhost:8000/api/auth/mp-login`,
      method: "POST",
      data: { code: loginRes.code },
    });
    const data = mpRes.data as any;
    if (!data.openid) throw new Error("微信登录失败");
    await userStore.wechatLogin({
      openid: data.openid,
      display_name: data.display_name || "微信用户",
    });
    // #endif

    // #ifdef H5
    // H5 开发模式：使用 mock openid（不依赖真实微信登录）
    await userStore.wechatLogin({
      openid: generateMockOpenid(),
      display_name: "微信用户" + Math.random().toString(36).slice(2, 6),
    });
    // #endif

    uni.reLaunch({ url: "/pages/index/index" });
  } catch (e: any) {
    uni.showToast({ title: e?.errMsg || "登录失败，请重试", icon: "none" });
  } finally {
    loading.value = false;
  }
}

function goAdminLogin() {
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
.wechat-btn:disabled { opacity: 0.5; }
.wechat-icon { margin-right: 8px; font-size: 20px; }
.agreement { text-align: center; margin-top: 16px; }
.agreement-label { display: flex; align-items: center; justify-content: center; gap: 4px; font-size: 13px; color: #606266; }
.checkbox { font-size: 18px; margin-right: 2px; color: #909399; }
.checkbox.checked { color: #07c160; }
.disclaimer { display: block; margin-top: 6px; font-size: 11px; color: #e6a23c; }
.link { color: #409eff; }
.admin-entry { margin-top: 30px; text-align: center; }
.admin-entry text { font-size: 14px; color: #409eff; }
</style>