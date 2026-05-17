<template>
  <view class="container">
    <text class="page-title">选择咨询师</text>
    <view v-if="counselors.length === 0" class="empty">暂无咨询师</view>
    <view
      v-for="c in counselors"
      :key="c.id"
      class="card"
      @click="selectCounselor(c)"
    >
      <view class="avatar">{{ c.display_name.charAt(0) }}</view>
      <view class="info">
        <text class="name">{{ c.display_name }}</text>
        <text class="phone" v-if="c.phone">{{ c.phone }}</text>
      </view>
      <text class="arrow">›</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getCounselors, type Counselor } from "@/api/appointment";

const counselors = ref<Counselor[]>([]);

onMounted(async () => {
  try {
    counselors.value = await getCounselors();
  } catch (e) {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
});

function selectCounselor(c: Counselor) {
  uni.navigateTo({ url: `/pages/booking/select?counselorId=${c.id}&name=${c.display_name}` });
}
</script>

<style lang="scss" scoped>
.container { padding: 16px; min-height: 100vh; background: #f5f5f5; }
.page-title { font-size: 20px; font-weight: bold; color: #303133; margin-bottom: 16px; display: block; }
.empty { text-align: center; color: #909399; padding: 40px 0; }
.card { display: flex; align-items: center; background: #fff; padding: 16px; border-radius: 10px; margin-bottom: 10px; }
.avatar { width: 44px; height: 44px; border-radius: 50%; background: #409eff; color: #fff; font-size: 18px; display: flex; align-items: center; justify-content: center; margin-right: 12px; flex-shrink: 0; }
.info { flex: 1; }
.name { font-size: 16px; color: #303133; display: block; margin-bottom: 4px; }
.phone { font-size: 13px; color: #909399; }
.arrow { font-size: 22px; color: #c0c4cc; }
</style>