import { defineStore } from "pinia";
import { ref } from "vue";
import type { UserInfo } from "@/api/auth";
import { login as loginApi, register as registerApi } from "@/api/auth";

export const useUserStore = defineStore("user", () => {
  const token = ref<string>(uni.getStorageSync("token") || "");
  const userInfo = ref<UserInfo | null>(
    uni.getStorageSync("userInfo") || null
  );

  async function login(username: string, password: string) {
    const res = await loginApi({ username, password });
    token.value = res.access_token;
    userInfo.value = res.user;
    uni.setStorageSync("token", res.access_token);
    uni.setStorageSync("userInfo", res.user);
  }

  async function register(params: {
    username: string;
    password: string;
    display_name: string;
    role: string;
    phone?: string;
  }) {
    const res = await registerApi(params);
    token.value = res.access_token;
    userInfo.value = res.user;
    uni.setStorageSync("token", res.access_token);
    uni.setStorageSync("userInfo", res.user);
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

  return { token, userInfo, login, register, logout, isLoggedIn };
});