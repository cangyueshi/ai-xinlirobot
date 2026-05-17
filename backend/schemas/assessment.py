from pydantic import BaseModel


class ScaleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    questions: list
    options: list


class AnswerSubmit(BaseModel):
    scale_id: int
    answers: list[dict]


class AssessmentResponse(BaseModel):
    id: int
    scale_id: int
    scale_name: str | None = None
    total_score: int
    result_level: str
    result_label: str | None = None
    result_detail: str | None = None
    created_at: str | None = None