import { request } from "@/utils/request";
import type { UserInfo } from "./auth";

export function getDashboard() {
  return request<{
    total_visitors: number;
    total_counselors: number;
    total_sessions: number;
    active_sessions: number;
  }>("/api/admin/dashboard");
}

export function getCounselors() {
  return request<UserInfo[]>("/api/admin/counselors");
}

export function createCounselor(data: {
  display_name: string;
  username: string;
  password: string;
  email?: string;
  bio?: string;
  specialties?: string;
}) {
  return request<UserInfo>("/api/admin/counselors", { method: "POST", data });
}

export function updateCounselor(id: number, data: any) {
  return request(`/api/admin/counselors/${id}`, { method: "PUT", data });
}

export function resetCounselorPassword(id: number, new_password: string) {
  return request(`/api/admin/counselors/${id}/reset-password`, {
    method: "POST",
    data: { new_password },
  });
}

export function disableCounselor(id: number) {
  return request(`/api/admin/counselors/${id}/disable`, { method: "POST" });
}

export function enableCounselor(id: number) {
  return request(`/api/admin/counselors/${id}/enable`, { method: "POST" });
}

export function deleteCounselor(id: number) {
  return request(`/api/admin/counselors/${id}`, { method: "DELETE" });
}

export function approveCounselor(id: number) {
  return request(`/api/admin/counselors/${id}/approve`, { method: "POST" });
}

export function rejectCounselor(id: number) {
  return request(`/api/admin/counselors/${id}/reject`, { method: "POST" });
}

export function getSubAdmins() {
  return request<UserInfo[]>("/api/admin/sub-admins");
}

export function createSubAdmin(data: {
  display_name: string;
  username: string;
  password: string;
  email?: string;
  permissions?: string;
}) {
  return request<UserInfo>("/api/admin/sub-admins", { method: "POST", data });
}

export function updateSubAdmin(id: number, data: any) {
  return request(`/api/admin/sub-admins/${id}`, { method: "PUT", data });
}

export function deleteSubAdmin(id: number) {
  return request(`/api/admin/sub-admins/${id}`, { method: "DELETE" });
}

export function getVisitors(keyword?: string) {
  const params = keyword ? `?keyword=${keyword}` : "";
  return request<UserInfo[]>(`/api/admin/visitors${params}`);
}

export function exportVisitors() {
  return request("/api/admin/export/visitors");
}

export function exportCounselors() {
  return request("/api/admin/export/counselors");
}

export function exportChatSessions() {
  return request("/api/admin/export/chat-sessions");
}

export function getExportLogs() {
  return request<any[]>("/api/admin/export-logs");
}