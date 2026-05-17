import { request } from "@/utils/request";

export interface ChatSession {
  id: number;
  visitor_id: number;
  counselor_id: number | null;
  status: string;
  risk_level: string;
  risk_summary: string | null;
  ai_summary: string | null;
  alert_sent: boolean;
  is_crisis_mode: boolean;
  crisis_level: string | null;
  user_message_count: number;
  ending_reason: string | null;
  created_at: string | null;
}

export interface ChatMessage {
  id: number;
  session_id: number;
  role: string;
  content: string;
  session_ended?: boolean;
  ending_reason?: string;
  crisis_alert?: boolean;
  crisis_level?: string;
  crisis_cancelled?: boolean;
  created_at: string | null;
}

export interface RiskAlert {
  id: number;
  session_id: number;
  visitor_id: number;
  level: string;
  crisis_level: string | null;
  summary: string;
  is_read: boolean;
  created_at: string | null;
}

export function createSession(): Promise<ChatSession> {
  return request("/api/chat/sessions", { method: "POST" });
}

export function sendMessage(
  sessionId: number,
  content: string
): Promise<ChatMessage> {
  return request(`/api/chat/sessions/${sessionId}/message`, {
    method: "POST",
    data: { content },
  });
}

export function endSession(sessionId: number): Promise<ChatSession> {
  return request(`/api/chat/sessions/${sessionId}/end`, { method: "POST" });
}

export function getMySessions(): Promise<ChatSession[]> {
  return request("/api/chat/sessions/mine");
}

export function getSessionMessages(sessionId: number): Promise<ChatMessage[]> {
  return request(`/api/chat/sessions/${sessionId}/messages`);
}

export function getAlerts(): Promise<RiskAlert[]> {
  return request("/api/chat/alerts");
}

export function getAlertCount(): Promise<{ unread: number }> {
  return request("/api/chat/alerts/count");
}

export function markAlertRead(alertId: number): Promise<any> {
  return request(`/api/chat/alerts/${alertId}/read`, { method: "POST" });
}