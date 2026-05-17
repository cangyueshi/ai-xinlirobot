import json
from sqlalchemy.orm import Session
from models.assessment import Scale

PHQ9 = {
    "name": "PHQ-9 抑郁症筛查量表",
    "description": "过去两周内，以下问题困扰你的频率是？用于抑郁症初步筛查，总分27分。0-4=无抑郁，5-9=轻度，10-14=中度，15-19=中重度，20-27=重度",
    "questions": [
        {"id": 1, "text": "做事时提不起劲或没有兴趣"},
        {"id": 2, "text": "感到心情低落、沮丧或绝望"},
        {"id": 3, "text": "入睡困难、睡不安稳或睡眠过多"},
        {"id": 4, "text": "感觉疲倦或没有活力"},
        {"id": 5, "text": "食欲不振或吃太多"},
        {"id": 6, "text": "觉得自己很糟，或感到失败，或让自己或家人失望"},
        {"id": 7, "text": "对事物专注有困难，如阅读或看电视"},
        {"id": 8, "text": "动作或说话速度缓慢到别人可察觉，或比平日更烦躁、坐立不安"},
        {"id": 9, "text": "有不如死掉或用某种方式伤害自己的念头"},
    ],
    "options": [
        {"value": 0, "label": "完全不会"},
        {"value": 1, "label": "好几天"},
        {"value": 2, "label": "一半以上天数"},
        {"value": 3, "label": "几乎每天"},
    ],
    "scoring": {
        "ranges": [
            {"min": 0, "max": 4, "level": "none", "label": "无抑郁症状"},
            {"min": 5, "max": 9, "level": "yellow", "label": "轻度抑郁"},
            {"min": 10, "max": 14, "level": "yellow", "label": "中度抑郁"},
            {"min": 15, "max": 19, "level": "red", "label": "中重度抑郁"},
            {"min": 20, "max": 27, "level": "red", "label": "重度抑郁"},
        ],
        "high_risk_item": 9,
    },
}

GAD7 = {
    "name": "GAD-7 焦虑症筛查量表",
    "description": "过去两周内，以下问题困扰你的频率是？用于焦虑症初步筛查，总分21分。0-4=无焦虑，5-9=轻度，10-14=中度，15-21=重度",
    "questions": [
        {"id": 1, "text": "感觉紧张、焦虑或急切"},
        {"id": 2, "text": "无法停止或控制担忧"},
        {"id": 3, "text": "对各种各样的事情担忧过多"},
        {"id": 4, "text": "很难放松下来"},
        {"id": 5, "text": "由于不安而无法静坐"},
        {"id": 6, "text": "变得容易烦恼或急躁"},
        {"id": 7, "text": "感到似乎将有可怕的事情发生而害怕"},
    ],
    "options": [
        {"value": 0, "label": "完全不会"},
        {"value": 1, "label": "好几天"},
        {"value": 2, "label": "一半以上天数"},
        {"value": 3, "label": "几乎每天"},
    ],
    "scoring": {
        "ranges": [
            {"min": 0, "max": 4, "level": "none", "label": "无焦虑症状"},
            {"min": 5, "max": 9, "level": "yellow", "label": "轻度焦虑"},
            {"min": 10, "max": 14, "level": "yellow", "label": "中度焦虑"},
            {"min": 15, "max": 21, "level": "red", "label": "重度焦虑"},
        ],
    },
}


def seed_scales(db: Session):
    existing = db.query(Scale).count()
    if existing > 0:
        return

    for data in [PHQ9, GAD7]:
        scale = Scale(
            name=data["name"],
            description=data["description"],
            questions_json=json.dumps(data["questions"], ensure_ascii=False),
            scoring_rules_json=json.dumps(
                {"options": data["options"], "scoring": data["scoring"]},
                ensure_ascii=False,
            ),
        )
        db.add(scale)
    db.commit()