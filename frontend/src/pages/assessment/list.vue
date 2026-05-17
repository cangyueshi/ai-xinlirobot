<template>
  <view class="container">
    <text class="page-title">心理测评</text>
    <text class="subtitle">选择量表进行心理健康自评，结果仅咨询师可见</text>

    <view v-if="scales.length === 0" class="empty">暂无可用量表</view>

    <view v-for="s in scales" :key="s.id" class="card" @click="startScale(s)">
      <text class="card-title">{{ s.name }}</text>
      <text class="card-desc">{{ s.description }}</text>
      <view class="card-footer">
        <text class="count">共 {{ s.question_count }} 题</text>
        <text class="action">开始测评 ›</text>
      </view>
    </view>

    <view class="divider"></view>

    <view class="link-row" @click="goHistory">
      <text>查看历史测评记录 ›</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getScales, type Scale } from "@/api/assessment";

const scales = ref<Scale[]>([]);

onMounted(async () => {
  try {
    scales.value = await getScales();
  } catch (e) {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
});

function startScale(s: Scale) {
  uni.navigateTo({ url: `/pages/assessment/answer?scaleId=${s.id}&name=${encodeURIComponent(s.name)}` });
}

function goHistory() {
  uni.navigateTo({ url: "/pages/assessment/history" });
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.page-title { font-size: 22px; font-weight: bold; color: #303133; display: block; }
.subtitle { font-size: 13px; color: #909399; margin-top: 4px; margin-bottom: 18px; display: block; }
.empty { text-align: center; color: #909399; padding: 40px 0; }
.card { background: #fff; padding: 18px; border-radius: 12px; margin-bottom: 12px; }
.card-title { font-size: 17px; font-weight: bold; color: #303133; display: block; margin-bottom: 6px; }
.card-desc { font-size: 13px; color: #909399; line-height: 1.5; margin-bottom: 10px; display: block; }
.card-footer { display: flex; justify-content: space-between; align-items: center; }
.count { font-size: 12px; color: #c0c4cc; }
.action { font-size: 14px; color: #409eff; }
.divider { height: 1px; background: #e4e7ed; margin: 16px 0; }
.link-row { text-align: center; font-size: 14px; color: #409eff; padding: 10px 0; }
</style>