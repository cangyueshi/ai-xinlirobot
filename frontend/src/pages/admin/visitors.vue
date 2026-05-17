<template>
  <view class="container">
    <view class="header">
      <text class="page-title">来访者管理</text>
    </view>

    <view class="search-bar">
      <input class="search-input" v-model="keyword" placeholder="搜索昵称或OpenID" @confirm="doSearch" />
      <button class="search-btn" @click="doSearch">搜索</button>
    </view>

    <view v-if="visitors.length === 0" class="empty">暂无数据</view>

    <view v-for="v in visitors" :key="v.id" class="card">
      <text class="name">{{ v.display_name }}</text>
      <text class="info">OpenID: {{ v.openid?.slice(0, 20) }}...</text>
      <text class="info">注册时间: {{ v.created_at || '-' }}</text>
      <text class="status" :class="v.status">{{ v.status === 'active' ? '正常' : v.status === 'disabled' ? '已禁用' : '已删除' }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getVisitors } from "@/api/admin";

const visitors = ref<any[]>([]);
const keyword = ref("");

onMounted(loadData);

async function loadData() {
  try { visitors.value = await getVisitors(); } catch {}
}

async function doSearch() {
  try { visitors.value = await getVisitors(keyword.value); } catch {}
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.header { margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: bold; color: #303133; }
.search-bar { display: flex; gap: 8px; margin-bottom: 16px; }
.search-input { flex: 1; height: 40px; border: 1px solid #dcdfe6; border-radius: 8px; padding: 0 12px; font-size: 14px; background: #fff; }
.search-btn { background: #409eff; color: #fff; font-size: 14px; padding: 0 16px; height: 40px; line-height: 40px; border-radius: 8px; border: none; }
.empty { text-align: center; color: #909399; padding: 40px 0; }
.card { background: #fff; border-radius: 10px; padding: 14px; margin-bottom: 10px; }
.name { font-size: 16px; font-weight: bold; color: #303133; display: block; }
.info { font-size: 13px; color: #606266; display: block; margin-top: 4px; }
.status { font-size: 12px; padding: 2px 8px; border-radius: 4px; margin-top: 6px; display: inline-block; }
.status.active { color: #67c23a; background: #f0f9eb; }
.status.disabled { color: #e6a23c; background: #fdf6ec; }
</style>