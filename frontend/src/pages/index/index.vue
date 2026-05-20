<template>
  <view class="page">
    <!-- ========== 来访者入口弹窗 ========== -->
    <template v-if="isVisitor && showEntryDialog">
      <view class="entry-overlay">
        <view class="entry-dialog">
          <view class="entry-ornament">
            <view class="ornament-circle"></view>
            <view class="ornament-leaf"></view>
          </view>
          <view class="entry-welcome">
            <text class="entry-greeting">{{ display_name }}，欢迎你</text>
            <text class="entry-sub">今天想和我聊聊什么？</text>
          </view>

          <view class="entry-cards">
            <view class="entry-card card-book" @click="goBooking">
              <view class="entry-card-visual">
                <view class="entry-card-icon icon-cal">
                  <text class="icon-symbol">&#x2606;</text>
                </view>
              </view>
              <view class="entry-card-body">
                <text class="entry-card-title">预约咨询</text>
                <text class="entry-card-desc">选择专业咨询师，面对面沟通</text>
              </view>
              <text class="entry-card-arrow">&rarr;</text>
            </view>

            <view class="entry-card" @click="goChat">
              <view class="entry-card-visual">
                <view class="entry-card-icon icon-chat">
                  <text class="icon-symbol">&#x2763;</text>
                </view>
              </view>
              <view class="entry-card-body">
                <text class="entry-card-title">AI 倾诉</text>
                <text class="entry-card-desc">随时倾诉，获得即时情绪疏导</text>
              </view>
              <text class="entry-card-arrow">&rarr;</text>
            </view>
          </view>

          <text class="entry-dismiss" @click="closeEntryDialog">稍后再说</text>
        </view>
      </view>
    </template>

    <!-- ========== 首页主要内容 ========== -->
    <template v-else>
      <!-- 顶部用户区 -->
      <view class="top-section">
        <view class="top-bar">
          <view class="user-avatar">
            <text class="avatar-letter">{{ initial }}</text>
          </view>
          <view class="user-meta">
            <text class="user-name">{{ userStore.userInfo?.display_name || '用户' }}</text>
            <text class="user-role-tag">{{ roleLabel }}</text>
          </view>
        </view>

        <!-- 问候语 -->
        <view class="daily-words" v-if="isVisitor">
          <text class="daily-text">每一次倾诉，都是对自己的温柔</text>
        </view>
      </view>

      <!-- 测评通知栏 -->
      <view v-if="isVisitor && showAssessNotice" class="assess-notice">
        <view class="assess-notice-mark">
          <text class="assess-mark-symbol">&#x2713;</text>
        </view>
        <view class="assess-notice-body">
          <text class="assess-notice-title">未完成心理测评</text>
          <text class="assess-notice-desc">预约咨询师前需先完成评估量表</text>
        </view>
        <text class="assess-notice-btn" @click="goAssessment">去完成</text>
      </view>

      <!-- 功能菜单 -->
      <view class="menu-section" v-if="isVisitor">
        <text class="menu-section-title">功能</text>
        <view class="menu-grid">
          <view class="menu-tile" @click="goBooking">
            <view class="menu-tile-icon tile-book">
              <text class="tile-symbol">&#x2737;</text>
            </view>
            <text class="menu-tile-label">预约咨询</text>
          </view>
          <view class="menu-tile" @click="goChat">
            <view class="menu-tile-icon tile-chat">
              <text class="tile-symbol">&#x2737;</text>
            </view>
            <text class="menu-tile-label">AI 对话</text>
          </view>
          <view class="menu-tile" @click="goPage('/pages/appointments/list')">
            <view class="menu-tile-icon tile-list">
              <text class="tile-symbol">&#x2737;</text>
            </view>
            <text class="menu-tile-label">我的预约</text>
          </view>
          <view class="menu-tile" @click="goPage('/pages/assessment/list')">
            <view class="menu-tile-icon tile-assess">
              <text class="tile-symbol">&#x2737;</text>
            </view>
            <text class="menu-tile-label">心理测评</text>
          </view>
          <view class="menu-tile" @click="goPage('/pages/assessment/history')">
            <view class="menu-tile-icon tile-history">
              <text class="tile-symbol">&#x2737;</text>
            </view>
            <text class="menu-tile-label">测评记录</text>
          </view>
        </view>
      </view>

      <!-- 咨询师菜单 -->
      <view class="menu-section" v-if="isCounselor">
        <text class="menu-section-title">咨询师工作台</text>
        <view class="menu-list">
          <view class="menu-item" @click="goPage('/pages/counselor/dashboard')">
            <view class="menu-icon-wrap icon-home">
              <text class="menu-icon-symbol">&#x2302;</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">工作台</text>
              <text class="menu-desc">咨询师工作台</text>
            </view>
            <text class="menu-arrow">&rsaquo;</text>
          </view>
          <view class="menu-item" @click="goPage('/pages/availability/manage')">
            <view class="menu-icon-wrap icon-clock">
              <text class="menu-icon-symbol">&#x23F0;</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">排班管理</text>
              <text class="menu-desc">设置可预约时间</text>
            </view>
            <text class="menu-arrow">&rsaquo;</text>
          </view>
          <view class="menu-item" @click="goPage('/pages/appointments/list')">
            <view class="menu-icon-wrap icon-appt">
              <text class="menu-icon-symbol">&#x2637;</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">来访者预约</text>
              <text class="menu-desc">查看和管理预约</text>
            </view>
            <text class="menu-arrow">&rsaquo;</text>
          </view>
          <view class="menu-item" @click="goPage('/pages/counselor/visitors')">
            <view class="menu-icon-wrap icon-visitors">
              <text class="menu-icon-symbol">&#x263C;</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">来访者信息</text>
              <text class="menu-desc">查看来访者信息</text>
            </view>
            <text class="menu-arrow">&rsaquo;</text>
          </view>
          <view class="menu-item" @click="goPage('/pages/counselor/assignScale')">
            <view class="menu-icon-wrap icon-scale">
              <text class="menu-icon-symbol">&#x2702;</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">分发量表</text>
              <text class="menu-desc">指定来访者完成测评</text>
            </view>
            <text class="menu-arrow">&rsaquo;</text>
          </view>
          <view class="menu-item" @click="goPage('/pages/chat/alerts')">
            <view class="menu-icon-wrap icon-alert">
              <text class="menu-icon-symbol">&#x26A0;</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">风险预警</text>
              <text class="menu-desc">查看危机预警</text>
            </view>
            <text class="menu-arrow">&rsaquo;</text>
          </view>
        </view>
      </view>

      <!-- 管理员菜单 -->
      <view class="menu-section" v-if="isAdmin">
        <text class="menu-section-title">管理</text>
        <view class="menu-list">
          <view class="menu-item" @click="goPage('/pages/admin/dashboard')">
            <view class="menu-icon-wrap icon-admin">
              <text class="menu-icon-symbol">&#x2699;</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">管理后台</text>
              <text class="menu-desc">系统管理首页</text>
            </view>
            <text class="menu-arrow">&rsaquo;</text>
          </view>
          <view class="menu-item" v-if="isSuperAdmin" @click="goPage('/pages/admin/counselors')">
            <view class="menu-icon-wrap icon-staff">
              <text class="menu-icon-symbol">&#x263A;</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">咨询师管理</text>
              <text class="menu-desc">管理咨询师账号</text>
            </view>
            <text class="menu-arrow">&rsaquo;</text>
          </view>
          <view class="menu-item" v-if="isSuperAdmin" @click="goPage('/pages/admin/sub-admins')">
            <view class="menu-icon-wrap icon-sub">
              <text class="menu-icon-symbol">&#x263D;</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">次级管理员</text>
              <text class="menu-desc">管理次级管理员</text>
            </view>
            <text class="menu-arrow">&rsaquo;</text>
          </view>
          <view class="menu-item" v-if="isAdmin" @click="goPage('/pages/admin/visitors')">
            <view class="menu-icon-wrap icon-users">
              <text class="menu-icon-symbol">&#x263C;</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">来访者管理</text>
              <text class="menu-desc">管理来访者账号</text>
            </view>
            <text class="menu-arrow">&rsaquo;</text>
          </view>
        </view>
      </view>

      <!-- 退出登录 -->
      <view class="menu-section">
        <view class="menu-item menu-logout" @click="handleLogout">
          <view class="menu-icon-wrap icon-exit">
            <text class="menu-icon-symbol">&#x2192;</text>
          </view>
          <view class="menu-content">
            <text class="menu-title logout-text">退出登录</text>
            <text class="menu-desc">退出当前账号</text>
          </view>
          <text class="menu-arrow">&rsaquo;</text>
        </view>
      </view>

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
  if (isVisitor.value && !skipEntryDialog.value) {
    setTimeout(() => {
      showEntryDialog.value = true;
    }, 300);
  }
  checkAssessmentStatus();
});

async function checkAssessmentStatus() {
  try {
    const result = await checkPrerequisites();
    showAssessNotice.value = !result.ready;
  } catch {}
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
// ====================================================
//  Warm Amber - 温暖琥珀配色系统
// ====================================================
$bg-main:       #FDF8F4;
$bg-card:       #FFFFFF;
$bg-soft:       #F8F2EC;

$primary:       #D4956A;
$primary-dark:  #B87A52;
$primary-light: #F0DCC8;
$primary-pale:  #F8EDE2;

$text-primary:  #3D322A;
$text-secondary:#8A8275;
$text-muted:    #B5A99A;

$accent-gold:   #D4A76A;
$accent-gold-light: #F0E3D0;

$border-soft:   #E8E0D0;
$border-light:  #F2ECE4;

$shadow-card:   0 2px 12px rgba(61, 50, 42, 0.05);
$shadow-raised: 0 6px 24px rgba(61, 50, 42, 0.08);
$shadow-soft:   0 2px 8px rgba(61, 50, 42, 0.03);

$radius-card:   20px;
$radius-item:   16px;
$radius-pill:   30px;

$font-stack:    -apple-system, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;

// ====================================================
//  Base
// ====================================================
.page {
  min-height: 100vh;
  background: $bg-main;
  padding: 0 20px;
  font-family: $font-stack;
  -webkit-font-smoothing: antialiased;
}

// ====================================================
//  入口弹窗 - 温暖欢迎界面
// ====================================================
.entry-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(150deg, #FDF8F4 0%, #F8EDE2 50%, #F0E3D0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  animation: fadeIn 0.5s ease;
}

.entry-dialog {
  width: calc(100% - 56px);
  max-width: 340px;
  background: $bg-card;
  border-radius: 28px;
  padding: 40px 28px 28px;
  position: relative;
  animation: slideUpFade 0.5s ease;
}

.entry-ornament {
  position: absolute;
  top: -1px;
  right: 28px;
  width: 80px;
  height: 50px;
  overflow: hidden;
}

.ornament-circle {
  position: absolute;
  top: -24px;
  right: -10px;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: $primary-pale;
  opacity: 0.6;
}

.ornament-leaf {
  position: absolute;
  top: 8px;
  right: 16px;
  width: 18px;
  height: 28px;
  border-radius: 50% 50% 50% 0;
  background: $primary-light;
  transform: rotate(-15deg);
  opacity: 0.5;
}

.entry-welcome {
  text-align: center;
  margin-bottom: 28px;
}

.entry-greeting {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: $text-primary;
  letter-spacing: 0.01em;
  margin-bottom: 8px;
}

.entry-sub {
  display: block;
  font-size: 14px;
  color: $text-secondary;
  letter-spacing: 0.02em;
}

//  入口卡片
.entry-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.entry-card {
  display: flex;
  align-items: center;
  padding: 18px 20px;
  border-radius: $radius-item;
  background: $bg-main;
  border: 1px solid $border-light;
  transition: all 0.2s ease;
  cursor: pointer;
}

.entry-card:active {
  transform: scale(0.98);
  border-color: $primary-light;
  background: $primary-pale;
}

.entry-card-visual {
  margin-right: 16px;
  flex-shrink: 0;
}

.entry-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.icon-chat {
  background: $primary-pale;
}

.card-book .entry-card-icon {
  background: $accent-gold-light;
}

.icon-symbol {
  font-size: 18px;
  color: $primary;
}

.card-book .icon-symbol {
  color: $accent-gold;
}

.entry-card-body {
  flex: 1;
}

.entry-card-title {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 3px;
}

.entry-card-desc {
  display: block;
  font-size: 12px;
  color: $text-secondary;
  line-height: 1.4;
}

.entry-card-arrow {
  font-size: 16px;
  color: $text-muted;
  margin-left: 8px;
  transition: transform 0.2s ease;
}

.entry-card:active .entry-card-arrow {
  transform: translateX(3px);
}

.entry-dismiss {
  display: block;
  text-align: center;
  font-size: 13px;
  color: $text-muted;
  margin-top: 20px;
  padding: 8px 0;
}

// ====================================================
//  顶部用户区
// ====================================================
.top-section {
  padding-top: 24px;
  animation: fadeInUp 0.4s ease;
}

.top-bar {
  display: flex;
  align-items: center;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, $primary, $primary-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 14px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba($primary-dark, 0.2);
}

.avatar-letter {
  font-size: 20px;
  color: #fff;
  font-weight: 600;
  letter-spacing: 0;
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

.user-role-tag {
  font-size: 11px;
  color: $primary;
  background: $primary-light;
  padding: 3px 12px;
  border-radius: 10px;
  display: inline-block;
  margin-top: 4px;
  font-weight: 500;
  letter-spacing: 0.02em;
}

//  每日寄语
.daily-words {
  margin-top: 16px;
  padding: 14px 18px;
  background: linear-gradient(135deg, $primary-pale, $accent-gold-light);
  border-radius: $radius-item;
  border: 1px solid rgba($primary, 0.1);
}

.daily-text {
  font-size: 14px;
  color: $text-primary;
  line-height: 1.6;
  letter-spacing: 0.03em;
  font-weight: 400;
  display: block;
  text-align: center;
  font-style: italic;
}

// ====================================================
//  测评通知栏
// ====================================================
.assess-notice {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #FBF5E8;
  border: 1px solid #E8DCC8;
  border-radius: $radius-item;
  padding: 14px 16px;
  margin-top: 16px;
  animation: fadeInUp 0.4s ease;
}

.assess-notice-mark {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: $accent-gold-light;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.assess-mark-symbol {
  font-size: 14px;
  color: $accent-gold;
  font-weight: 700;
}

.assess-notice-body {
  flex: 1;
}

.assess-notice-title {
  font-size: 13px;
  font-weight: 600;
  color: #A0853A;
  display: block;
  margin-bottom: 2px;
}

.assess-notice-desc {
  font-size: 12px;
  color: #B8A06A;
  display: block;
  line-height: 1.4;
}

.assess-notice-btn {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: $accent-gold;
  padding: 7px 16px;
  border-radius: $radius-pill;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}

.assess-notice-btn:active {
  opacity: 0.85;
}

// ====================================================
//  功能菜单 - 来访者网格
// ====================================================
.menu-section {
  margin-top: 24px;
  animation: fadeInUp 0.4s ease;
}

.menu-section-title {
  font-size: 13px;
  color: $text-muted;
  font-weight: 500;
  display: block;
  margin-bottom: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.menu-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.menu-tile {
  background: $bg-card;
  padding: 24px 16px 18px;
  border-radius: $radius-card;
  text-align: center;
  box-shadow: $shadow-card;
  transition: all 0.2s ease;
  cursor: pointer;
  border: 1px solid transparent;
}

.menu-tile:active {
  transform: scale(0.96);
  border-color: $primary-light;
  box-shadow: $shadow-soft;
}

.menu-tile-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  transition: all 0.2s ease;
}

.tile-chat {
  background: $primary-pale;
}

.tile-book {
  background: $accent-gold-light;
}

.tile-list {
  background: #EDE8E8;
}

.tile-assess {
  background: #E8EAF0;
}

.tile-history {
  background: #E8EDEA;
}

.tile-symbol {
  font-size: 18px;
  color: $primary;
  font-weight: 700;
}

.tile-list .tile-symbol {
  color: $text-secondary;
}

.tile-history .tile-symbol {
  color: $primary;
}

.menu-tile-label {
  font-size: 13px;
  font-weight: 500;
  color: $text-primary;
  display: block;
  letter-spacing: 0.02em;
}

// ====================================================
//  菜单列表 - 咨询师/管理员
// ====================================================
.menu-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.menu-item {
  display: flex;
  align-items: center;
  background: $bg-card;
  padding: 14px 18px;
  border-radius: $radius-item;
  box-shadow: $shadow-card;
  transition: all 0.15s ease;
  cursor: pointer;
  border: 1px solid transparent;
}

.menu-item:active {
  transform: scale(0.98);
  border-color: $border-light;
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
  transition: all 0.2s ease;
}

.icon-home { background: $primary-pale; }
.icon-clock { background: #F0EDE8; }
.icon-appt { background: #E8EAF0; }
.icon-visitors { background: #EDE8E8; }
.icon-scale { background: #E8EDEA; }
.icon-alert { background: $primary-pale; }
.icon-admin { background: #E8EDEA; }
.icon-staff { background: #EDE8E8; }
.icon-sub { background: #F0EDE8; }
.icon-users { background: #E8EAF0; }
.icon-exit { background: #F5EAE8; }

.menu-icon-symbol {
  font-size: 16px;
  font-weight: 400;
}

.icon-home .menu-icon-symbol { color: $primary; }
.icon-clock .menu-icon-symbol { color: $text-secondary; }
.icon-appt .menu-icon-symbol { color: $text-secondary; }
.icon-visitors .menu-icon-symbol { color: $text-secondary; }
.icon-scale .menu-icon-symbol { color: $primary; }
.icon-alert .menu-icon-symbol { color: $accent-gold; }
.icon-admin .menu-icon-symbol { color: $primary; }
.icon-staff .menu-icon-symbol { color: $text-secondary; }
.icon-sub .menu-icon-symbol { color: $text-secondary; }
.icon-users .menu-icon-symbol { color: $text-secondary; }
.icon-exit .menu-icon-symbol { color: #C48070; }

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
  font-size: 22px;
  color: $text-muted;
  margin-left: 8px;
  font-weight: 300;
}

.menu-logout {
  margin-top: 4px;
}

.logout-text {
  color: #C48070;
}

.bottom-safe {
  height: 32px;
}

// ====================================================
//  动画
// ====================================================
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUpFade {
  from {
    opacity: 0;
    transform: translateY(28px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

//  Entrance staggers
.assess-notice { animation-delay: 0.1s; }
.menu-section:nth-of-type(1) { animation-delay: 0.15s; }
.menu-section:nth-of-type(2) { animation-delay: 0.2s; }
.menu-section:nth-of-type(3) { animation-delay: 0.25s; }
</style>
