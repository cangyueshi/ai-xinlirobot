import { request } from "@/utils/request";

export interface Availability {
  id: number;
  counselor_id: number;
  date: string;
  start_time: string;
  end_time: string;
  is_booked: boolean;
}

export interface Appointment {
  id: number;
  availability_id: number;
  backup_availability_id: number | null;
  counselor_id: number;
  visitor_id: number;
  visitor_name: string | null;
  counselor_name: string | null;
  date: string;
  start_time: string;
  end_time: string;
  status: string;
  notes: string | null;
  confirmed_at: string | null;
  created_at: string | null;
}

export interface Counselor {
  id: number;
  display_name: string;
  specialties?: string;
  bio?: string;
  phone: string | null;
}

export interface PrerequisitesResult {
  ready: boolean;
  missing_scales: { scale_id: number; name: string }[];
  completed_scales: { scale_id: number; name: string; result_level: string; total_score: number }[];
}

export function getCounselors(): Promise<Counselor[]> {
  return request("/api/appointments/counselors");
}

export function checkPrerequisites(): Promise<PrerequisitesResult> {
  return request("/api/appointments/prerequisites");
}

export function getCounselorAvailabilities(
  counselorId: number,
  date?: string
): Promise<Availability[]> {
  const params = date ? `?d=${date}` : "";
  return request(`/api/appointments/availabilities/${counselorId}${params}`);
}

export function bookAppointment(data: {
  availability_id: number;
  backup_availability_id?: number;
  reason?: string;
}): Promise<Appointment> {
  return request("/api/appointments/book", {
    method: "POST",
    data,
  });
}

export function getMyAppointments(): Promise<Appointment[]> {
  return request("/api/appointments/mine");
}

export function cancelAppointment(aptId: number): Promise<any> {
  return request(`/api/appointments/${aptId}/cancel`, { method: "POST" });
}

export function confirmAppointment(aptId: number): Promise<any> {
  return request(`/api/appointments/${aptId}/confirm`, { method: "POST" });
}

export function setAvailabilities(data: {
  date: string;
  time_slots: { start_time: string; end_time: string }[];
}): Promise<any> {
  return request("/api/appointments/availabilities/batch", {
    method: "POST",
    data,
  });
}

export function getMyAvailabilities(date?: string): Promise<Availability[]> {
  const params = date ? `?d=${date}` : "";
  return request(`/api/appointments/availabilities/mine${params}`);
}