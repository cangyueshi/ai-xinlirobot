<template>
  <view class="container">
    <view class="progress-bar">
      <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
      <text class="progress-text">{{ currentIndex + 1 }} / {{ questions.length }}</text>
    </view>

    <view class="question-card">
      <text class="q-num">第 {{ currentIndex + 1 }} 题</text>
      <text class="q-text">{{ currentQuestion?.text }}</text>

      <view class="options">
        <view
          v-for="opt in options"
          :key="opt.value"
          class="option"
          :class="{ selected: answers[currentIndex]?.value === opt.value }"
          @click="selectOption(opt.value)"
        >
          <text>{{ opt.label }}</text>
        </view>
      </view>
    </view>

    <view class="nav-btns">
      <button v-if="currentIndex > 0" class="btn-prev" @click="prev">上一题</button>
      <button
        v-if="currentIndex < questions.length - 1"
        class="btn-next"
        :disabled="answers[currentIndex] === undefined"
        @click="next"
      >
        下一题
      </button>
      <button
        v-if="currentIndex === questions.length - 1"
        class="btn-submit"
        :disabled="answers[currentIndex] === undefined || submitting"
        @click="submit"
      >
        {{ submitting ? "提交中..." : "提交" }}
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { getScaleDetail, submitAssessment } from "@/api/assessment";

const scaleId = ref(0);
const scaleName = ref("");
const questions = ref<{ id: number; text: string }[]>([]);
const options = ref<{ value: number; label: string }[]>([]);
const currentIndex = ref(0);
const answers = ref<{ id: number; value: number }[]>([]);
const submitting = ref(false);

const currentQuestion = computed(() => questions.value[currentIndex.value]);
const progressPercent = computed(() =>
  questions.value.length ? ((currentIndex.value + 1) / questions.value.length) * 100 : 0
);

onMounted(async () => {
  const pages = getCurrentPages();
  const opts = (pages[pages.length - 1].options as any);
  scaleId.value = Number(opts.scaleId);
  scaleName.value = decodeURIComponent(opts.name || "");

  try {
    const detail = await getScaleDetail(scaleId.value);
    questions.value = detail.questions;
    options.value = detail.options;
  } catch (e) {
    uni.showToast({ title: "加载失败", icon: "none" });
  }
});

function selectOption(value: number) {
  answers.value[currentIndex.value] = {
    id: questions.value[currentIndex.value].id,
    value,
  };
}

function next() {
  if (answers.value[currentIndex.value] === undefined) {
    uni.showToast({ title: "请先选择答案", icon: "none" });
    return;
  }
  currentIndex.value++;
}

function prev() {
  currentIndex.value--;
}

async function submit() {
  if (answers.value.length < questions.value.length) {
    uni.showToast({ title: "请完成所有题目", icon: "none" });
    return;
  }
  submitting.value = true;
  try {
    const result = await submitAssessment({
      scale_id: scaleId.value,
      answers: answers.value,
    });
    // 存入本地存储，避免 URL 传参丢数据
    uni.setStorageSync("lastAssessmentResult", result);
    uni.redirectTo({ url: "/pages/assessment/result" });
  } catch (e: any) {
    uni.showToast({ title: e.detail || "提交失败", icon: "none" });
  } finally {
    submitting.value = false;
  }
}
</script>

<style lang="scss" scoped>
.container { padding: 0; min-height: 100vh; background: #f5f5f5; }
.progress-bar { display: flex; align-items: center; background: #fff; padding: 12px 16px; border-bottom: 1px solid #eee; }
.progress-fill { height: 4px; background: #409eff; border-radius: 2px; }
.progress-text { font-size: 12px; color: #909399; margin-left: 10px; flex-shrink: 0; }
.question-card { padding: 24px 20px; }
.q-num { font-size: 13px; color: #909399; display: block; margin-bottom: 10px; }
.q-text { font-size: 18px; color: #303133; font-weight: 500; line-height: 1.6; display: block; margin-bottom: 24px; }
.options { display: flex; flex-direction: column; gap: 10px; }
.option { padding: 14px 16px; border: 1.5px solid #dcdfe6; border-radius: 10px; font-size: 15px; color: #606266; text-align: center; }
.option.selected { border-color: #409eff; background: #ecf5ff; color: #409eff; font-weight: 500; }
.nav-btns { display: flex; justify-content: space-between; padding: 16px 20px; gap: 12px; }
.btn-prev { flex: 1; height: 44px; line-height: 44px; background: #f5f5f5; color: #606266; border-radius: 8px; font-size: 15px; border: 1px solid #dcdfe6; }
.btn-next { flex: 1; height: 44px; line-height: 44px; background: #409eff; color: #fff; border-radius: 8px; font-size: 15px; border: none; }
.btn-submit { flex: 1; height: 44px; line-height: 44px; background: #67c23a; color: #fff; border-radius: 8px; font-size: 15px; border: none; }
.btn-next[disabled], .btn-submit[disabled] { opacity: 0.5; }
</style>