<template>
  <view class="container">
    <view class="header">
      <text class="title">创建账号</text>
      <text class="subtitle">选择你的角色，开始使用</text>
    </view>

    <view class="form">
      <view class="form-item">
        <text class="label">用户名</text>
        <input
          class="input"
          v-model="form.username"
          placeholder="3-50位字符"
        />
      </view>

      <view class="form-item">
        <text class="label">显示名称</text>
        <input
          class="input"
          v-model="form.display_name"
          placeholder="你的称呼"
        />
      </view>

      <view class="form-item">
        <text class="label">手机号（选填）</text>
        <input
          class="input"
          v-model="form.phone"
          placeholder="便于咨询师联系"
        />
      </view>

      <view class="form-item">
        <text class="label">角色</text>
        <picker
          mode="selector"
          :range="roleOptions"
          @change="onRoleChange"
        >
          <view class="picker">
            {{ form.role ? roleLabelMap[form.role] : "请选择角色" }}
          </view>
        </picker>
      </view>

      <view class="form-item">
        <text class="label">密码</text>
        <input
          class="input"
          v-model="form.password"
          type="password"
          placeholder="至少6位"
        />
      </view>

      <view class="form-item">
        <text class="label">确认密码</text>
        <input
          class="input"
          v-model="confirmPassword"
          type="password"
          placeholder="再次输入密码"
        />
      </view>

      <button class="btn" :disabled="loading" @click="handleRegister">
        {{ loading ? "注册中..." : "注册" }}
      </button>

      <view class="link" @click="goLogin">
        已有账号？去登录
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useUserStore } from "@/store/user";

const userStore = useUserStore();
const loading = ref(false);
const confirmPassword = ref("");

const roleOptions = ["来访者", "咨询师"];
const roleValueMap: Record<string, string> = {
  "来访者": "visitor",
  "咨询师": "counselor",
};
const roleLabelMap: Record<string, string> = {
  visitor: "来访者",
  counselor: "咨询师",
};

const form = reactive({
  username: "",
  display_name: "",
  phone: "",
  role: "visitor",
  password: "",
});

function onRoleChange(e: any) {
  const index = e.detail.value;
  form.role = roleValueMap[roleOptions[index]];
}

async function handleRegister() {
  if (!form.username || !form.display_name || !form.password) {
    uni.showToast({ title: "请填写必填信息", icon: "none" });
    return;
  }
  if (form.password.length < 6) {
    uni.showToast({ title: "密码至少6位", icon: "none" });
    return;
  }
  if (form.password !== confirmPassword.value) {
    uni.showToast({ title: "两次密码不一致", icon: "none" });
    return;
  }

  loading.value = true;
  try {
    await userStore.register({
      username: form.username,
      password: form.password,
      display_name: form.display_name,
      role: form.role,
      phone: form.phone || undefined,
    });
    uni.showToast({ title: "注册成功", icon: "success" });
    setTimeout(() => {
      uni.reLaunch({ url: "/pages/index/index" });
    }, 500);
  } catch (e: any) {
    uni.showToast({ title: e.detail || e.message || "注册失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

function goLogin() {
  uni.navigateBack();
}
</script>

<style lang="scss" scoped>
.container {
  padding: 40px 30px;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 40px;

  .title {
    display: block;
    font-size: 26px;
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 8px;
  }

  .subtitle {
    display: block;
    font-size: 14px;
    color: #909399;
  }
}

.form {
  .form-item {
    margin-bottom: 18px;

    .label {
      display: block;
      font-size: 14px;
      color: #606266;
      margin-bottom: 6px;
    }

    .input {
      width: 100%;
      height: 42px;
      padding: 0 15px;
      font-size: 15px;
      border: 1px solid #dcdfe6;
      border-radius: 8px;
      box-sizing: border-box;
      background: #fff;
    }

    .picker {
      width: 100%;
      height: 42px;
      line-height: 42px;
      padding: 0 15px;
      font-size: 15px;
      border: 1px solid #dcdfe6;
      border-radius: 8px;
      box-sizing: border-box;
      background: #fff;
      color: #606266;
    }
  }

  .btn {
    width: 100%;
    height: 48px;
    line-height: 48px;
    font-size: 18px;
    color: #fff;
    background: #67c23a;
    border-radius: 8px;
    margin-top: 25px;
    border: none;
  }

  .btn[disabled] {
    background: #b3e19d;
  }

  .link {
    text-align: center;
    margin-top: 18px;
    font-size: 14px;
    color: #409eff;
  }
}
</style>