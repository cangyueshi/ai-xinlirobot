import { request } from "@/utils/request";

export interface UserInfo {
  id: number;
  username: string | null;
  openid: string | null;
  display_name: string;
  role: "admin" | "counselor" | "visitor";
  phone: string | null;
  is_active: boolean;
}

export interface WechatLoginParams {
  openid: string;
  display_name: string;
  role: string;
  phone?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

export function wechatLogin(params: WechatLoginParams): Promise<AuthResponse> {
  return request<AuthResponse>("/api/auth/wechat-login", {
    method: "POST",
    data: params,
  });
}

export function getCurrentUser(): Promise<UserInfo> {
  return request<UserInfo>("/api/auth/me");
}