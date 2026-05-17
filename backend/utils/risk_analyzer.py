import re
from models.chat import RiskLevel

HIGH_RISK_PATTERNS = [
    r"想.*死",
    r"不想.*活",
    r"结束.*生命",
    r"自杀",
    r"自残",
    r"自伤",
    r"割腕",
    r"跳楼",
    r"上吊",
    r"安眠药.*吃",
    r"我不在了.*好",
    r"消失.*世界",
    r"伤害.*自己",
    r"杀了.*自己",
    r"活不下",
    r"没意[思义].*活",
]

MEDIUM_RISK_PATTERNS = [
    r"失眠|睡不[着好]",
    r"抑郁|情绪低落|心情不好",
    r"焦虑|紧张.*不行",
    r"想.*哭|哭.*停不下",
    r"不想.*上课|不想.*见人",
    r"没有.*希望|看不到.*未来",
    r"觉得.*孤独|没人.*理解",
    r"压力.*大|承受不了",
    r"崩溃",
    r"绝望",
    r"活着.*累|活着.*没意思",
    r"想.*离开",
    r"不想.*说话|不想.*出门",
]


def analyze_risk(messages: list[dict]) -> dict:
    full_text = " ".join([m.get("content", "") for m in messages])

    for pattern in HIGH_RISK_PATTERNS:
        if re.search(pattern, full_text):
            return {
                "level": RiskLevel.RED,
                "summary": "检测到高危信号，来访者可能表达自杀或自残倾向，建议立即人工介入",
            }

    medium_matches = []
    for pattern in MEDIUM_RISK_PATTERNS:
        if re.search(pattern, full_text):
            medium_matches.append(pattern.replace(r".*", "...").replace(r"\\", ""))

    if medium_matches:
        return {
            "level": RiskLevel.YELLOW,
            "summary": f"检测到中度风险信号，涉及：{', '.join(medium_matches[:3])}。建议咨询师关注",
        }

    return {"level": RiskLevel.NONE, "summary": ""}