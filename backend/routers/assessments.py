import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.assessment import Scale, Assessment, RiskLevel
from schemas.assessment import AnswerSubmit
from utils.deps import get_current_user, require_role

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


@router.get("/scales")
def list_scales(db: Session = Depends(get_db)):
    scales = db.query(Scale).filter(Scale.is_active == 1).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "question_count": len(json.loads(s.questions_json)),
        }
        for s in scales
    ]


@router.get("/scales/{scale_id}")
def get_scale(scale_id: int, db: Session = Depends(get_db)):
    scale = db.query(Scale).filter(Scale.id == scale_id, Scale.is_active == 1).first()
    if not scale:
        raise HTTPException(status_code=404, detail="量表不存在")

    rules = json.loads(scale.scoring_rules_json)
    return {
        "id": scale.id,
        "name": scale.name,
        "description": scale.description,
        "questions": json.loads(scale.questions_json),
        "options": rules["options"],
    }


@router.post("/submit")
def submit_assessment(
    data: AnswerSubmit,
    current_user: User = Depends(require_role("visitor")),
    db: Session = Depends(get_db),
):
    scale = db.query(Scale).filter(Scale.id == data.scale_id, Scale.is_active == 1).first()
    if not scale:
        raise HTTPException(status_code=404, detail="量表不存在")

    rules = json.loads(scale.scoring_rules_json)
    answers = data.answers

    total_score = sum(a.get("value", 0) for a in answers)

    level = RiskLevel.NONE
    label = "正常范围"
    for r in rules["scoring"]["ranges"]:
        if r["min"] <= total_score <= r["max"]:
            level = RiskLevel(r["level"])
            label = r["label"]
            break

    high_risk_item = rules["scoring"].get("high_risk_item")
    high_risk_answered = False
    if high_risk_item:
        for a in answers:
            if a.get("id") == high_risk_item and a.get("value", 0) > 0:
                high_risk_answered = True
                break

    if high_risk_answered and level != RiskLevel.RED:
        level = RiskLevel.RED
        label = "注意：自杀意念条目阳性"

    assessment = Assessment(
        visitor_id=current_user.id,
        scale_id=scale.id,
        answers_json=json.dumps(answers, ensure_ascii=False),
        total_score=total_score,
        result_level=level,
        result_detail=f"{scale.name} | 总分 {total_score} | {label}",
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return {
        "id": assessment.id,
        "scale_id": scale.id,
        "scale_name": scale.name,
        "total_score": total_score,
        "result_level": level.value,
        "result_label": label,
        "result_detail": assessment.result_detail,
        "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
    }


@router.get("/mine")
def get_my_assessments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = (
        db.query(Assessment, Scale.name)
        .join(Scale, Assessment.scale_id == Scale.id)
        .filter(Assessment.visitor_id == current_user.id)
        .order_by(Assessment.created_at.desc())
        .all()
    )
    return [
        {
            "id": a.id,
            "scale_id": a.scale_id,
            "scale_name": scale_name,
            "total_score": a.total_score,
            "result_level": a.result_level.value if a.result_level else "none",
            "result_label": a.result_detail.split("|")[-1].strip() if a.result_detail else "",
            "result_detail": a.result_detail,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a, scale_name in results
    ]