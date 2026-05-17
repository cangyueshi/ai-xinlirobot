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
  counselor_id: number;
  visitor_id: number;
  date: string;
  start_time: string;
  end_time: string;
  status: string;
  notes: string | null;
  created_at: string | null;
}

export interface Counselor {
  id: number;
  display_name: string;
  phone: string | null;
}

export function getCounselors(): Promise<Counselor[]> {
  return request("/api/appointments/counselors");
}

export function getCounselorAvailabilities(
  counselorId: number,
  date?: string
): Promise<Availability[]> {
  const params = date ? `?d=${date}` : "";
  return request(`/api/appointments/availabilities/${counselorId}${params}`);
}

export function bookAppointment(availabilityId: number): Promise<Appointment> {
  return request("/api/appointments/book", {
    method: "POST",
    data: { availability_id: availabilityId },
  });
}

export function getMyAppointments(): Promise<Appointment[]> {
  return request("/api/appointments/mine");
}

export function cancelAppointment(aptId: number): Promise<any> {
  return request(`/api/appointments/${aptId}/cancel`, { method: "POST" });
}

export function addAvailability(data: {
  date: string;
  start_time: string;
  end_time: string;
}): Promise<Availability> {
  return request("/api/appointments/availabilities", {
    method: "POST",
    data,
  });
}

export function addAvailabilityBatch(data: {
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

export function deleteAvailability(avId: number): Promise<any> {
  return request(`/api/appointments/availabilities/${avId}`, {
    method: "DELETE",
  });
}