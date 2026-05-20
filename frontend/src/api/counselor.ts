import { request } from "@/utils/request";

export interface DashboardData {
  upcoming_appointments: number;
  unread_alerts: number;
  total_visitors: number;
  total_chat_sessions: number;
  recent_sessions: {
    id: number;
    visitor_id: number;
    risk_level: string;
    ai_summary: string;
    updated_at: string | null;
  }[];
}

export interface VisitorInfo {
  id: number;
  display_name: string;
  phone: string | null;
  chat_count: number;
  assessment_count: number;
}

export function getDashboard(): Promise<DashboardData> {
  return request("/api/counselor/dashboard");
}

export function getAllSessions(risk?: string): Promise<any[]> {
  const params = risk ? `?risk=${risk}` : "";
  return request(`/api/counselor/sessions${params}`);
}

export function getAllVisitors(): Promise<VisitorInfo[]> {
  return request("/api/counselor/visitors");
}

export function getVisitorAssessments(visitorId: number): Promise<any[]> {
  return request(`/api/counselor/visitors/${visitorId}/assessments`);
}

export function getVisitorSessions(visitorId: number): Promise<any[]> {
  return request(`/api/counselor/visitors/${visitorId}/sessions`);
}

export interface ScaleInfo {
  id: number;
  name: string;
  description: string;
  question_count: number;
}

export interface ScaleAssignment {
  id: number;
  visitor_id: number;
  visitor_name: string;
  scale_id: number;
  scale_name: string;
  status: string;
  created_at: string | null;
}

export function getCounselorScales(): Promise<ScaleInfo[]> {
  return request("/api/counselor/scales");
}

export function getScaleAssignments(): Promise<ScaleAssignment[]> {
  return request("/api/counselor/scale-assignments");
}

export function createScaleAssignment(visitorId: number, scaleId: number): Promise<any> {
  return request(`/api/counselor/scale-assignments?visitor_id=${visitorId}&scale_id=${scaleId}`, {
    method: "POST",
  });
}

export function deleteScaleAssignment(assignmentId: number): Promise<any> {
  return request(`/api/counselor/scale-assignments/${assignmentId}`, {
    method: "DELETE",
  });
}