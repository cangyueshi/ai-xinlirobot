<template>
  <view class="container">
    <text class="page-title">测评记录</text>

    <view v-if="list.length === 0" class="empty">暂无测评记录</view>

    <view v-for="a in list" :key="a.id" class="card">
      <view class="row">
        <text class="name">{{ a.scale_name }}</text>
        <text class="tag" :class="a.result_level">
          {{ a.result_level === "red" ? "需关注" : a.result_level === "yellow" ? "轻度" : "正常" }}
        </text>
      </view>
      <text class="detail">总分 {{ a.total_score }} · {{ a.result_label }}</text>
      <text class="time">{{ formatDate(a.created_at) }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getMyAssessments } from "@/api/assessment";

const list = ref<any[]>([]);

onMounted(async () => {
  try {
    list.value = await getMyAssessments();
  } catch (e) {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
});

function formatDate(d: string | null) {
  if (!d) return "";
  return d.slice(0, 16).replace("T", " ");
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.page-title { font-size: 20px; font-weight: bold; color: #303133; margin-bottom: 14px; display: block; }
.empty { text-align: center; color: #909399; padding: 40px 0; }
.card { background: #fff; padding: 14px 16px; border-radius: 10px; margin-bottom: 10px; }
.row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.name { font-size: 15px; font-weight: 500; color: #303133; }
.tag { font-size: 12px; padding: 2px 8px; border-radius: 4px; }
.tag.none { color: #67c23a; background: #f0f9eb; }
.tag.yellow { color: #e6a23c; background: #fdf6ec; }
.tag.red { color: #f56c6c; background: #fef0f0; }
.detail { font-size: 13px; color: #606266; display: block; margin-bottom: 4px; }
.time { font-size: 12px; color: #c0c4cc; }
</style>