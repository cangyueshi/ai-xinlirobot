<template>
  <view class="container">
    <view class="card">
      <text class="title">修改密码</text>
      <text class="hint" v-if="isForce">首次登录，请修改初始密码</text>

      <view class="form-group">
        <text class="label">新密码</text>
        <input class="input" v-model="newPassword" type="password" placeholder="至少6位字符" />
      </view>

      <view class="form-group">
        <text class="label">确认新密码</text>
        <input class="input" v-model="confirmPassword" type="password" placeholder="再次输入新密码" />
      </view>

      <button class="btn" @click="doChange" :loading="loading">确认修改</button>
      <text class="link" @click="skip">暂不修改，直接进入</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { changePassword } from "@/api/auth";

const isForce = ref(false);
const newPassword = ref("");
const confirmPassword = ref("");
const loading = ref(false);

onLoad((options: any) => {
  isForce.value = options.force === "1";
});

async function doChange() {
  if (!newPassword.value || newPassword.value.length < 6) {
    uni.showToast({ title: "密码至少6位", icon: "none" });
    return;
  }
  if (newPassword.value !== confirmPassword.value) {
    uni.showToast({ title: "两次密码不一致", icon: "none" });
    return;
  }
  loading.value = true;
  try {
    await changePassword({ old_password: undefined, new_password: newPassword.value });
    uni.showToast({ title: "密码修改成功", icon: "success" });
    setTimeout(() => uni.reLaunch({ url: "/pages/index/index" }), 800);
  } catch (e: any) {
    uni.showToast({ title: e.detail || "修改失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

function skip() {
  uni.reLaunch({ url: "/pages/index/index" });
}
</script>

<style lang="scss" scoped>
.container {
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh; background: #f5f5f5; padding: 20px;
}
.card { width: 100%; max-width: 360px; background: #fff; border-radius: 12px; padding: 28px 22px; }
.title { font-size: 22px; font-weight: bold; color: #303133; display: block; text-align: center; }
.hint { font-size: 13px; color: #e6a23c; display: block; text-align: center; margin-top: 8px; margin-bottom: 20px; }
.form-group { margin-top: 18px; }
.label { font-size: 14px; color: #606266; display: block; margin-bottom: 6px; }
.input { width: 100%; height: 44px; padding: 0 12px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 15px; box-sizing: border-box; }
.btn { width: 100%; height: 44px; line-height: 44px; background: #409eff; color: #fff; border-radius: 8px; font-size: 16px; margin-top: 24px; border: none; }
.link { font-size: 13px; color: #909399; text-align: center; display: block; margin-top: 14px; }
</style>