import { defineStore } from "pinia";
import { ref } from "vue";
import type { UserInfo } from "@/api/auth";
import { wechatLogin as wechatLoginApi, adminLogin as adminLoginApi } from "@/api/auth";

export const useUserStore = defineStore("user", () => {
  const token = ref<string>(uni.getStorageSync("token") || "");
  const userInfo = ref<UserInfo | null>(uni.getStorageSync("userInfo") || null);

  async function wechatLogin(params: { openid: string; display_name: string; avatar_url?: string }) {
    const res = await wechatLoginApi(params);
    token.value = res.access_token;
    userInfo.value = res.user;
    uni.setStorageSync("token", res.access_token);
    uni.setStorageSync("userInfo", res.user);
    uni.setStorageSync("openid", params.openid);
  }

  async function adminLogin(params: { username: string; password: string }) {
    const res = await adminLoginApi(params);
    token.value = res.access_token;
    userInfo.value = res.user;
    uni.setStorageSync("token", res.access_token);
    uni.setStorageSync("userInfo", res.user);
    return res;
  }

  function logout() {
    token.value = "";
    userInfo.value = null;
    uni.removeStorageSync("token");
    uni.removeStorageSync("userInfo");
    uni.reLaunch({ url: "/pages/login/login" });
  }

  function isLoggedIn() {
    return !!token.value;
  }

  return { token, userInfo, wechatLogin, adminLogin, logout, isLoggedIn };
});