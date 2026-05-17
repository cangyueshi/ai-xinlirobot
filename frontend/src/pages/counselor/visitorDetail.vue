<template>
  <view class="container">
    <text class="page-title">{{ visitorName }}</text>

    <view class="tabs">
      <view class="tab" :class="{ active: tab === 'chat' }" @click="tab = 'chat'">对话记录</view>
      <view class="tab" :class="{ active: tab === 'assessment' }" @click="tab = 'assessment'">测评记录</view>
    </view>

    <view v-if="tab === 'chat'">
      <view v-if="sessions.length === 0" class="empty">暂无对话记录</view>
      <view v-for="s in sessions" :key="s.id" class="card" @click="viewChat(s.id)">
        <view class="row">
          <text class="s-tag" :class="s.risk_level">{{ riskLabel(s.risk_level) }}</text>
          <text class="s-time">{{ fmtTime(s.created_at) }}</text>
        </view>
        <text class="s-summary">{{ s.ai_summary || '暂无摘要' }}</text>
      </view>
    </view>

    <view v-if="tab === 'assessment'">
      <view v-if="assessments.length === 0" class="empty">暂无测评记录</view>
      <view v-for="a in assessments" :key="a.id" class="card">
        <view class="row">
          <text class="scale-name">{{ a.scale_name }}</text>
          <text class="a-tag" :class="a.result_level">{{ riskLabel(a.result_level) }}</text>
        </view>
        <text class="a-detail">总分 {{ a.total_score }} · {{ a.result_detail }}</text>
        <text class="s-time">{{ fmtTime(a.created_at) }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getVisitorSessions, getVisitorAssessments } from "@/api/counselor";

const visitorId = ref(0);
const visitorName = ref("");
const tab = ref("chat");
const sessions = ref<any[]>([]);
const assessments = ref<any[]>([]);

onMounted(async () => {
  const pages = getCurrentPages();
  const opts = (pages[pages.length - 1].options as any);
  visitorId.value = Number(opts.id);
  visitorName.value = decodeURIComponent(opts.name || "");

  try {
    [sessions.value, assessments.value] = await Promise.all([
      getVisitorSessions(visitorId.value),
      getVisitorAssessments(visitorId.value),
    ]);
  } catch (e) {}
});

function riskLabel(l: string) {
  return l === "red" ? "高危" : l === "yellow" ? "中度" : "正常";
}

function fmtTime(t: string | null) {
  if (!t) return "";
  return t.slice(0, 16).replace("T", " ");
}

function viewChat(id: number) {
  uni.navigateTo({ url: `/pages/chat/detail?id=${id}` });
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.page-title { font-size: 20px; font-weight: bold; color: #303133; margin-bottom: 14px; display: block; }
.tabs { display: flex; background: #fff; border-radius: 10px; margin-bottom: 14px; overflow: hidden; }
.tab { flex: 1; text-align: center; padding: 12px 0; font-size: 14px; color: #909399; }
.tab.active { color: #409eff; font-weight: bold; border-bottom: 2px solid #409eff; }
.empty { text-align: center; color: #909399; padding: 30px 0; font-size: 14px; }
.card { background: #fff; padding: 14px 16px; border-radius: 10px; margin-bottom: 8px; }
.row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.s-tag, .a-tag { font-size: 12px; padding: 1px 8px; border-radius: 4px; }
.s-tag.red, .a-tag.red { color: #f56c6c; background: #fef0f0; }
.s-tag.yellow, .a-tag.yellow { color: #e6a23c; background: #fdf6ec; }
.s-tag.none, .a-tag.none { color: #67c23a; background: #f0f9eb; }
.s-time { font-size: 12px; color: #c0c4cc; }
.s-summary { font-size: 13px; color: #606266; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.scale-name { font-size: 14px; color: #303133; font-weight: 500; }
.a-detail { font-size: 13px; color: #606266; display: block; margin-top: 4px; }
</style>