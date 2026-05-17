<template>
  <view class="container">
    <view class="header">
      <view class="logo">🧠</view>
      <text class="title">AI 心理咨询机器人</text>
      <text class="subtitle">专业心理筛查与陪伴平台</text>
    </view>

    <view class="wechat-section">
      <button class="wechat-btn" @click="handleWechatAuth" :disabled="loading">
        <text class="wechat-icon">💚</text>
        <text>{{ loading ? '授权中...' : '微信一键登录' }}</text>
      </button>
      <text class="tip">首次使用将自动创建账号</text>
    </view>

    <!-- 首次使用：补充信息弹窗 -->
    <view v-if="showInfoForm" class="overlay" @click.self="showInfoForm = false">
      <view class="form-box">
        <text class="form-title">完善信息</text>
        <view class="form-item">
          <text class="label">昵称</text>
          <input class="input" v-model="form.display_name" placeholder="怎么称呼你？" />
        </view>
        <view class="form-item">
          <text class="label">身份</text>
          <picker mode="selector" :range="roles" @change="onRoleChange">
            <view class="picker">{{ form.roleLabel || '选择身份' }}</view>
          </picker>
        </view>
        <button class="submit-btn" @click="submitInfo" :disabled="!form.display_name">
          确认登录
        </button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { wechatLogin } from "@/api/auth";
import { useUserStore } from "@/store/user";

const userStore = useUserStore();
const loading = ref(false);
const showInfoForm = ref(false);
const roles = ["我是来访者", "我是咨询师"];
const roleMap: Record<string, string> = { "我是来访者": "visitor", "我是咨询师": "counselor" };

const form = reactive({
  display_name: "",
  role: "visitor",
  roleLabel: "我是来访者",
});

function onRoleChange(e: any) {
  const label = roles[e.detail.value];
  form.roleLabel = label;
  form.role = roleMap[label];
}

function handleWechatAuth() {
  showInfoForm.value = true;
}

async function submitInfo() {
  if (!form.display_name.trim()) {
    uni.showToast({ title: "请输入昵称", icon: "none" });
    return;
  }
  loading.value = true;
  try {
    const openid = "wx_h5_sim_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8);
    await userStore.wechatLogin({
      openid,
      display_name: form.display_name.trim(),
      role: form.role,
    });
    uni.showToast({ title: "登录成功", icon: "success" });
    setTimeout(() => uni.reLaunch({ url: "/pages/index/index" }), 500);
  } catch (e: any) {
    uni.showToast({ title: "登录失败，请重试", icon: "none" });
  } finally {
    loading.value = false;
  }
}
</script>

<style lang="scss" scoped>
.container { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; padding: 40px; background: linear-gradient(135deg, #e8f4fd 0%, #f0f5ff 100%); }
.header { text-align: center; margin-bottom: 60px; }
.logo { font-size: 64px; margin-bottom: 16px; }
.title { display: block; font-size: 26px; font-weight: bold; color: #2c3e50; margin-bottom: 8px; }
.subtitle { font-size: 14px; color: #909399; }
.wechat-section { width: 100%; text-align: center; }
.wechat-btn { width: 100%; height: 52px; background: #07c160; color: #fff; border-radius: 12px; font-size: 17px; display: flex; align-items: center; justify-content: center; gap: 8px; border: none; }
.wechat-btn[disabled] { background: #a0e8bf; }
.wechat-icon { font-size: 22px; }
.tip { display: block; font-size: 12px; color: #c0c4cc; margin-top: 14px; }

.overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.form-box { background: #fff; width: 85%; border-radius: 16px; padding: 24px; }
.form-title { font-size: 20px; font-weight: bold; color: #303133; text-align: center; display: block; margin-bottom: 20px; }
.form-item { margin-bottom: 16px; }
.label { display: block; font-size: 14px; color: #606266; margin-bottom: 6px; }
.input { width: 100%; height: 42px; padding: 0 12px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 15px; box-sizing: border-box; }
.picker { width: 100%; height: 42px; line-height: 42px; padding: 0 12px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 15px; color: #606266; box-sizing: border-box; }
.submit-btn { width: 100%; height: 46px; line-height: 46px; background: #07c160; color: #fff; border-radius: 8px; font-size: 16px; margin-top: 8px; border: none; }
.submit-btn[disabled] { background: #a0e8bf; }
</style>