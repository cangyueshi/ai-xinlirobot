import { request } from "@/utils/request";

export interface Scale {
  id: number;
  name: string;
  description: string;
  question_count: number;
}

export interface ScaleDetail {
  id: number;
  name: string;
  description: string;
  questions: { id: number; text: string }[];
  options: { value: number; label: string }[];
}

export interface AssessmentResult {
  id: number;
  scale_id: number;
  scale_name: string;
  total_score: number;
  result_level: string;
  result_label: string;
  result_detail: string | null;
  created_at: string | null;
}

export function getScales(): Promise<Scale[]> {
  return request("/api/assessments/scales");
}

export function getScaleDetail(scaleId: number): Promise<ScaleDetail> {
  return request(`/api/assessments/scales/${scaleId}`);
}

export function submitAssessment(data: {
  scale_id: number;
  answers: { id: number; value: number }[];
}): Promise<AssessmentResult> {
  return request("/api/assessments/submit", {
    method: "POST",
    data: { scale_id: data.scale_id, answers: data.answers },
  });
}

export function getMyAssessments(): Promise<AssessmentResult[]> {
  return request("/api/assessments/mine");
}