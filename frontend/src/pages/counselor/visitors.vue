<template>
  <view class="container">
    <text class="page-title">来访者管理</text>

    <view v-if="visitors.length === 0" class="empty">暂无来访者</view>

    <view v-for="v in visitors" :key="v.id" class="card" @click="viewVisitor(v)">
      <view class="avatar">{{ v.display_name.charAt(0) }}</view>
      <view class="info">
        <text class="name">{{ v.display_name }}</text>
        <text class="phone" v-if="v.phone">{{ v.phone }}</text>
        <view class="counts">
          <text>💬 {{ v.chat_count }} 次对话</text>
          <text style="margin-left:12px">📝 {{ v.assessment_count }} 次测评</text>
        </view>
      </view>
      <text class="arrow">›</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getAllVisitors, type VisitorInfo } from "@/api/counselor";

const visitors = ref<VisitorInfo[]>([]);

onMounted(async () => {
  try {
    visitors.value = await getAllVisitors();
  } catch (e) {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
});

function viewVisitor(v: VisitorInfo) {
  uni.navigateTo({
    url: `/pages/counselor/visitorDetail?id=${v.id}&name=${encodeURIComponent(v.display_name)}`,
  });
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.page-title { font-size: 20px; font-weight: bold; color: #303133; margin-bottom: 14px; display: block; }
.empty { text-align: center; color: #909399; padding: 40px 0; }
.card { display: flex; align-items: center; background: #fff; padding: 16px; border-radius: 10px; margin-bottom: 10px; }
.avatar { width: 44px; height: 44px; border-radius: 50%; background: #409eff; color: #fff; font-size: 18px; display: flex; align-items: center; justify-content: center; margin-right: 12px; flex-shrink: 0; }
.info { flex: 1; }
.name { font-size: 16px; color: #303133; display: block; }
.phone { font-size: 13px; color: #909399; display: block; margin-bottom: 4px; }
.counts { font-size: 12px; color: #909399; }
.arrow { font-size: 22px; color: #c0c4cc; }
</style>