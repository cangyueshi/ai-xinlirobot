<template>
  <view class="container">
    <view class="header">
      <text class="title">AI 心理咨询机器人</text>
      <text class="subtitle">专业心理筛查与陪伴平台</text>
    </view>

    <view class="form">
      <view class="form-item">
        <text class="label">用户名</text>
        <input
          class="input"
          v-model="form.username"
          placeholder="请输入用户名"
        />
      </view>

      <view class="form-item">
        <text class="label">密码</text>
        <input
          class="input"
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
        />
      </view>

      <button class="btn" :disabled="loading" @click="handleLogin">
        {{ loading ? "登录中..." : "登录" }}
      </button>

      <view class="link" @click="goRegister">
        还没有账号？立即注册
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useUserStore } from "@/store/user";

const userStore = useUserStore();
const loading = ref(false);

const form = reactive({
  username: "",
  password: "",
});

async function handleLogin() {
  if (!form.username || !form.password) {
    uni.showToast({ title: "请填写完整信息", icon: "none" });
    return;
  }

  loading.value = true;
  try {
    await userStore.login(form.username, form.password);
    uni.showToast({ title: "登录成功", icon: "success" });
    setTimeout(() => {
      uni.reLaunch({ url: "/pages/index/index" });
    }, 500);
  } catch (e: any) {
    uni.showToast({ title: e.detail || "登录失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

function goRegister() {
  uni.navigateTo({ url: "/pages/register/register" });
}
</script>

<style lang="scss" scoped>
.container {
  padding: 40px 30px;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 50px;

  .title {
    display: block;
    font-size: 28px;
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 10px;
  }

  .subtitle {
    display: block;
    font-size: 14px;
    color: #909399;
  }
}

.form {
  .form-item {
    margin-bottom: 20px;

    .label {
      display: block;
      font-size: 14px;
      color: #606266;
      margin-bottom: 8px;
    }

    .input {
      width: 100%;
      height: 44px;
      padding: 0 15px;
      font-size: 16px;
      border: 1px solid #dcdfe6;
      border-radius: 8px;
      box-sizing: border-box;
      background: #fff;
    }
  }

  .btn {
    width: 100%;
    height: 48px;
    line-height: 48px;
    font-size: 18px;
    color: #fff;
    background: #409eff;
    border-radius: 8px;
    margin-top: 30px;
    border: none;
  }

  .btn[disabled] {
    background: #a0cfff;
  }

  .link {
    text-align: center;
    margin-top: 20px;
    font-size: 14px;
    color: #409eff;
  }
}
</style>