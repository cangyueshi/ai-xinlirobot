<template>
  <view class="page">
    <!-- ========== 来访者入口弹窗（取代首页内容） ========== -->
    <template v-if="isVisitor && showEntryDialog">
      <view class="entry-screen">
        <view class="entry-dialog">
          <view class="entry-greeting">{{ display_name }}，欢迎你</view>
          <view class="entry-sub">今天想做什么？</view>

          <view class="entry-cards">
            <view class="entry-card card-ai" @click="goChat">
              <view class="card-icon-wrap">
                <text class="card-icon">💬</text>
              </view>
              <view class="card-info">
                <text class="card-title">与 AI 心理咨询师对话</text>
                <text class="card-desc">随时随地倾诉，获得即时情绪疏导</text>
              </view>
              <text class="card-arrow">→</text>
            </view>

            <view class="entry-card card-book" @click="goBooking">
              <view class="card-icon-wrap">
                <text class="card-icon">📅</text>
              </view>
              <view class="card-info">
                <text class="card-title">预约心理咨询师</text>
                <text class="card-desc">选择专业咨询师，安排面对面沟通</text>
              </view>
              <text class="card-arrow">→</text>
            </view>
          </view>

          <text class="entry-dismiss" @click="closeEntryDialog">稍后再说</text>
        </view>
      </view>
    </template>

    <!-- ========== 首页主要内容（弹窗关闭后可见） ========== -->
    <template v-else>
      <!-- ========== 顶部用户卡片 ========== -->
      <view class="top-bar">
        <view class="user-avatar">
          <text class="avatar-letter">{{ initial }}</text>
        </view>
        <view class="user-meta">
          <text class="user-name">{{ userStore.userInfo?.display_name || '用户' }}</text>
          <text class="user-role">{{ roleLabel }}</text>
        </view>
      </view>

      <!-- ========== 测评通知栏（来访者未完成必测量表时显示） ========== -->
      <view v-if="isVisitor && showAssessNotice" class="assess-notice">
        <text class="assess-notice-icon">📌</text>
        <view class="assess-notice-body">
          <text class="assess-notice-title">您还未完成心理测评</text>
          <text class="assess-notice-desc">预约咨询师前需先完成 GAD-7 和 PHQ-9 量表</text>
        </view>
        <text class="assess-notice-btn" @click="goAssessment">立即测评</text>
      </view>

      <!-- ========== 菜单列表 ========== -->
      <view class="menu-section">
        <text class="section-label">功能菜单</text>

      <view class="menu-list">
        <!-- 来访者菜单 -->
        <template v-if="isVisitor">
          <view class="menu-item" @click="goChat">
            <view class="menu-icon-wrap" style="background:#e8f5e9;">
              <text class="menu-icon" style="color:#4caf50;">💬</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">AI 对话</text>
              <text class="menu-desc">即时情绪疏导</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>

          <view class="menu-item" @click="goBooking">
            <view class="menu-icon-wrap" style="background:#fff3e0;">
              <text class="menu-icon" style="color:#ff9800;">📅</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">预约咨询师</text>
              <text class="menu-desc">预约专业心理咨询</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>

          <view class="menu-item" @click="goPage('/pages/appointments/list')">
            <view class="menu-icon-wrap" style="background:#fce4ec;">
              <text class="menu-icon" style="color:#e91e63;">📌</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">我的预约</text>
              <text class="menu-desc">查看预约记录</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>

          <view class="menu-item" @click="goPage('/pages/assessment/list')">
            <view class="menu-icon-wrap" style="background:#f3e5f5;">
              <text class="menu-icon" style="color:#9c27b0;">📝</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">心理测评</text>
              <text class="menu-desc">专业心理量表评估</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>

          <view class="menu-item" @click="goPage('/pages/assessment/history')">
            <view class="menu-icon-wrap" style="background:#e0f2f1;">
              <text class="menu-icon" style="color:#009688;">📈</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">测评记录</text>
              <text class="menu-desc">查看历史结果</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>
        </template>

        <!-- 咨询师菜单 -->
        <template v-if="isCounselor">
          <view class="menu-item" @click="goPage('/pages/counselor/dashboard')">
            <view class="menu-icon-wrap" style="background:#e8f5e9;">
              <text class="menu-icon" style="color:#4caf50;">🏠</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">工作台</text>
              <text class="menu-desc">咨询师工作台</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>

          <view class="menu-item" @click="goPage('/pages/availability/manage')">
            <view class="menu-icon-wrap" style="background:#fff3e0;">
              <text class="menu-icon" style="color:#ff9800;">⏰</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">管理可预约时间</text>
              <text class="menu-desc">设置一周排班</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>

          <view class="menu-item" @click="goPage('/pages/appointments/list')">
            <view class="menu-icon-wrap" style="background:#e3f2fd;">
              <text class="menu-icon" style="color:#2196f3;">📊</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">来访者预约</text>
              <text class="menu-desc">查看和管理预约</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>

          <view class="menu-item" @click="goPage('/pages/counselor/visitors')">
            <view class="menu-icon-wrap" style="background:#fce4ec;">
              <text class="menu-icon" style="color:#e91e63;">👥</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">来访者信息中心</text>
              <text class="menu-desc">查看来访者信息与记录</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>

          <view class="menu-item" @click="goPage('/pages/counselor/assignScale')">
            <view class="menu-icon-wrap" style="background:#f3e5f5;">
              <text class="menu-icon" style="color:#9c27b0;">📋</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">分发量表</text>
              <text class="menu-desc">指定来访者完成测评量表</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>

          <view class="menu-item" @click="goPage('/pages/chat/alerts')">
            <view class="menu-icon-wrap" style="background:#fce4ec;">
              <text class="menu-icon" style="color:#f44336;">🔔</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">风险预警</text>
              <text class="menu-desc">查看危机预警</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>
        </template>

        <!-- 管理员菜单 -->
        <template v-if="isAdmin">
          <view class="menu-item" @click="goPage('/pages/admin/dashboard')">
            <view class="menu-icon-wrap" style="background:#e3f2fd;">
              <text class="menu-icon" style="color:#2196f3;">⚙️</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">管理后台</text>
              <text class="menu-desc">系统管理首页</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>

          <view class="menu-item" v-if="isSuperAdmin" @click="goPage('/pages/admin/counselors')">
            <view class="menu-icon-wrap" style="background:#e8f5e9;">
              <text class="menu-icon" style="color:#4caf50;">👩‍⚕️</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">咨询师管理</text>
              <text class="menu-desc">管理咨询师账号</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>

          <view class="menu-item" v-if="isSuperAdmin" @click="goPage('/pages/admin/sub-admins')">
            <view class="menu-icon-wrap" style="background:#fff3e0;">
              <text class="menu-icon" style="color:#ff9800;">👤</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">次级管理员</text>
              <text class="menu-desc">管理次级管理员</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>

          <view class="menu-item" v-if="isAdmin" @click="goPage('/pages/admin/visitors')">
            <view class="menu-icon-wrap" style="background:#fce4ec;">
              <text class="menu-icon" style="color:#e91e63;">👥</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">来访者管理</text>
              <text class="menu-desc">管理来访者账号</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>
        </template>

        <!-- 退出登录 -->
        <view class="menu-item logout-item" @click="handleLogout">
          <view class="menu-icon-wrap" style="background:#fef0f0;">
            <text class="menu-icon" style="color:#f56c6c;">🚪</text>
          </view>
          <view class="menu-content">
            <text class="menu-title" style="color:#f56c6c;">退出登录</text>
            <text class="menu-desc">退出当前账号</text>
          </view>
          <text class="menu-arrow" style="color:#f56c6c;">›</text>
        </view>
      </view>
    </view>

    <!-- 底部安全区 -->
    <view class="bottom-safe"></view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { useUserStore } from "@/store/user";
import { checkPrerequisites } from "@/api/appointment";

const userStore = useUserStore();
const showEntryDialog = ref(false);
const showAssessNotice = ref(false);
const skipEntryDialog = ref(false);

onLoad((options) => {
  if (options?.from === "assessment") {
    skipEntryDialog.value = true;
  }
});

onMounted(() => {
  // 来访者登录后自动弹出入口对话框（测评完成返回时不弹）
  if (isVisitor.value && !skipEntryDialog.value) {
    setTimeout(() => {
      showEntryDialog.value = true;
    }, 300);
  }
  // 检查测评完成状态
  checkAssessmentStatus();
});

async function checkAssessmentStatus() {
  try {
    const result = await checkPrerequisites();
    showAssessNotice.value = !result.ready;
  } catch {
    // 静默失败，不阻塞首页加载
  }
}

const display_name = computed(() => userStore.userInfo?.display_name || '');

const initial = computed(() => {
  const name = userStore.userInfo?.display_name || "U";
  return name.charAt(0).toUpperCase();
});

const roleLabel = computed(() => {
  const labels: Record<string, string> = {
    super_admin: "超级管理员",
    sub_admin: "次级管理员",
    counselor: "咨询师",
    visitor: "来访者",
  };
  return labels[userStore.userInfo?.role || ""] || "用户";
});

const isVisitor = computed(() => userStore.userInfo?.role === "visitor");
const isCounselor = computed(() => userStore.userInfo?.role === "counselor");
const isAdmin = computed(() =>
  userStore.userInfo?.role === "super_admin" || userStore.userInfo?.role === "sub_admin"
);
const isSuperAdmin = computed(() => userStore.userInfo?.role === "super_admin");

function goPage(url: string) {
  uni.navigateTo({ url });
}

function goChat() {
  showEntryDialog.value = false;
  uni.navigateTo({ url: '/pages/chat/chat' });
}

function goBooking() {
  showEntryDialog.value = false;
  uni.navigateTo({ url: '/pages/booking/counselors' });
}

function closeEntryDialog() {
  showEntryDialog.value = false;
}

function goAssessment() {
  uni.navigateTo({ url: '/pages/assessment/list' });
}

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
// ====== 色彩变量 ======
$bg: #f5f3ef;
$card-bg: #ffffff;
$primary: #5b8c7e;
$primary-light: #e8f0ed;
$text-primary: #2c3e50;
$text-secondary: #7a8a8a;
$text-muted: #aab7b7;
$shadow: 0 2px 12px rgba(0,0,0,0.06);

.page {
  min-height: 100vh;
  background: $bg;
  padding: 0 16px;
}

// ====== 顶部用户卡片 ======
.top-bar {
  display: flex;
  align-items: center;
  padding: 20px 0 16px;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, $primary, #7dab9e);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 14px;
  flex-shrink: 0;
}

.avatar-letter {
  font-size: 20px;
  color: #fff;
  font-weight: 600;
}

.user-meta {
  flex: 1;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  color: $text-primary;
  display: block;
  line-height: 1.4;
}

.user-role {
  font-size: 12px;
  color: $primary;
  background: $primary-light;
  padding: 2px 10px;
  border-radius: 10px;
  display: inline-block;
  margin-top: 2px;
}

// ====== 来访者入口弹窗（全屏容器，取代首页） ======
.entry-screen {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(160deg, #f5f3ef, #e4efe9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  animation: fadeIn 0.4s ease;
}

.entry-dialog {
  width: calc(100% - 48px);
  max-width: 340px;
  background: #fff;
  border-radius: 24px;
  padding: 36px 24px 24px;
  animation: slideUp 0.4s ease;
}

.entry-greeting {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: $text-primary;
  text-align: center;
  margin-bottom: 6px;
}

.entry-sub {
  display: block;
  font-size: 14px;
  color: $text-secondary;
  text-align: center;
  margin-bottom: 28px;
}

.entry-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.entry-card {
  display: flex;
  align-items: center;
  padding: 18px 16px;
  border-radius: 16px;
  border: 1.5px solid transparent;
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
}

.entry-card:active {
  transform: scale(0.98);
}

.card-ai {
  background: #f0f7f4;
  border-color: #d0e3dc;
}

.card-book {
  background: #faf3ef;
  border-color: #eddcd2;
}

.card-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 14px;
  flex-shrink: 0;
  background: rgba(255,255,255,0.7);
}

.card-icon {
  font-size: 22px;
}

.card-info {
  flex: 1;
}

.card-title {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 3px;
}

.card-desc {
  display: block;
  font-size: 12px;
  color: $text-secondary;
  line-height: 1.4;
}

.card-arrow {
  font-size: 18px;
  color: $text-muted;
  margin-left: 8px;
}

.entry-dismiss {
  display: block;
  text-align: center;
  font-size: 13px;
  color: $text-muted;
  margin-top: 20px;
  padding: 8px 0;
}

// ====== 测评通知栏 ======
.assess-notice {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fdf6ec;
  border: 1px solid #f0d9a0;
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 12px;
}

.assess-notice-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.assess-notice-body {
  flex: 1;
  min-width: 0;
}

.assess-notice-title {
  font-size: 13px;
  font-weight: 600;
  color: #c0822e;
  display: block;
  margin-bottom: 2px;
}

.assess-notice-desc {
  font-size: 12px;
  color: #b08a5a;
  display: block;
  line-height: 1.4;
}

.assess-notice-btn {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: #e6a23c;
  padding: 6px 14px;
  border-radius: 16px;
  flex-shrink: 0;
}

.assess-notice-btn:active {
  opacity: 0.85;
}

// ====== 功能菜单 ======
.menu-section {
  margin-top: 8px;
}

.section-label {
  font-size: 13px;
  color: $text-secondary;
  font-weight: 500;
  display: block;
  margin-bottom: 10px;
  padding-left: 2px;
}

.menu-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.menu-item {
  display: flex;
  align-items: center;
  background: $card-bg;
  padding: 14px 16px;
  border-radius: 14px;
  box-shadow: $shadow;
  transition: transform 0.15s ease;
}

.menu-item:active {
  transform: scale(0.98);
}

.menu-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 14px;
  flex-shrink: 0;
}

.menu-icon {
  font-size: 18px;
}

.menu-content {
  flex: 1;
}

.menu-title {
  font-size: 15px;
  font-weight: 500;
  color: $text-primary;
  display: block;
  line-height: 1.3;
}

.menu-desc {
  font-size: 12px;
  color: $text-secondary;
  display: block;
  margin-top: 2px;
}

.menu-arrow {
  font-size: 20px;
  color: #d0d5d5;
  margin-left: 8px;
}

.logout-item {
  margin-top: 4px;
}

.bottom-safe {
  height: 32px;
}

// ====== 动画 ======
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
