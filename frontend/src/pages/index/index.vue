<template>
  <view class="container">
    <view class="user-card">
      <view class="avatar">
        <text class="avatar-text">{{ initial }}</text>
      </view>
      <view class="user-info">
        <text class="name">{{ userStore.userInfo?.display_name }}</text>
        <text class="role-tag">{{ roleLabel }}</text>
      </view>
    </view>

    <view class="menu-list">
      <view class="menu-item" v-if="isVisitor">
        <text class="menu-icon">💬</text>
        <text class="menu-text">开始 AI 对话</text>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" v-if="isVisitor">
        <text class="menu-icon">📋</text>
        <text class="menu-text">心理测评</text>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" v-if="isVisitor">
        <text class="menu-icon">📅</text>
        <text class="menu-text">预约咨询师</text>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" v-if="isCounselor">
        <text class="menu-icon">📊</text>
        <text class="menu-text">来访者管理</text>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" v-if="isCounselor">
        <text class="menu-icon">🔔</text>
        <text class="menu-text">风险预警</text>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" v-if="isAdmin">
        <text class="menu-icon">⚙️</text>
        <text class="menu-text">系统管理</text>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" @click="handleLogout">
        <text class="menu-icon">🚪</text>
        <text class="menu-text logout-text">退出登录</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useUserStore } from "@/store/user";

const userStore = useUserStore();

const initial = computed(() => {
  const name = userStore.userInfo?.display_name || "U";
  return name.charAt(0).toUpperCase();
});

const roleLabel = computed(() => {
  const labels: Record<string, string> = {
    admin: "管理员",
    counselor: "咨询师",
    visitor: "来访者",
  };
  return labels[userStore.userInfo?.role || ""] || "用户";
});

const isVisitor = computed(() => userStore.userInfo?.role === "visitor");
const isCounselor = computed(() => userStore.userInfo?.role === "counselor");
const isAdmin = computed(() => userStore.userInfo?.role === "admin");

function handleLogout() {
  uni.showModal({
    title: "提示",
    content: "确定要退出登录吗？",
    success: (res) => {
      if (res.confirm) {
        userStore.logout();
      }
    },
  });
}
</script>

<style lang="scss" scoped>
.container {
  padding: 20px 15px;
  min-height: 100vh;
}

.user-card {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

  .avatar {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: #409eff;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;

    .avatar-text {
      font-size: 24px;
      color: #fff;
      font-weight: bold;
    }
  }

  .user-info {
    .name {
      display: block;
      font-size: 18px;
      font-weight: bold;
      color: #2c3e50;
      margin-bottom: 4px;
    }

    .role-tag {
      display: inline-block;
      font-size: 12px;
      color: #409eff;
      background: #ecf5ff;
      padding: 2px 10px;
      border-radius: 10px;
    }
  }
}

.menu-list {
  .menu-item {
    display: flex;
    align-items: center;
    background: #fff;
    padding: 16px 18px;
    margin-bottom: 1px;
    border-radius: 8px;

    .menu-icon {
      font-size: 20px;
      margin-right: 14px;
    }

    .menu-text {
      flex: 1;
      font-size: 16px;
      color: #303133;
    }

    .menu-arrow {
      font-size: 20px;
      color: #c0c4cc;
    }

    .logout-text {
      color: #f56c6c;
    }
  }
}
</style>