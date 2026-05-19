import re
from models.chat import RiskLevel, CrisisLevel

LEVEL_1_KEYWORDS = [
    r"我现在.{0,5}想死",
    r"我已经.{0,5}准备.{0,3}自杀",
    r"(我在楼顶|站在楼顶|在楼顶上)",
    r"我.{0,3}买.{0,3}安眠药",
    r"我.{0,3}(要|想).{0,3}杀.{0,3}他",
    r"马上就[要会].{0,3}死",
    r"准备.*自[杀尽]",
    r"准备.{0,3}跳[楼下河]",
    r"现在.*就.*想.*死",
    r"马上.{0,3}(跳楼|跳下去|跳河)",
    r"已经.{0,3}吃.{0,5}(安眠药|过量.?药|很多.?药|一堆.?药)",
]

LEVEL_2_KEYWORDS = [
    r"我想死(?!你了|你|啦)",
    r"我.{0,3}活着.{0,3}没有意义",
    r"我真.{0,3}想.{0,3}一了百了",
    r"我想.{0,3}杀.{0,5}(他|她|人|那个人|那些人)",
    r"想.*自[杀尽]",
    r"一了百了",
    r"结束.*生命",
    r"自杀",
    r"割.{0,1}腕",
    r"跳[楼河]",
    r"上吊",
    r"安眠药",
]

LEVEL_3_KEYWORDS = [
    r"我觉得.{0,3}活着.{0,3}(好累|很累|太累)",
    r"我.{0,3}不想.{0,3}活",
    r"生活.{0,3}没有.{0,2}希望",
    r"我真.{0,3}想.{0,5}消失",
    r"从.{0,3}世界.{0,3}消失",
    r"活.{0,3}累",
    r"活.{0,3}没意[思义]",
    r"不想.{0,3}活",
    r"没[有.]{0,2}希望",
    r"看不到.{0,2}未来",
    r"想.*离开.*世界",
    r"消失.*世界",
    r"我.{0,3}(觉得|真|真的|就是).{0,5}没用",
    r"我.{0,3}(是|真|真是|就是).{0,5}负担",
    r"不如.{0,2}死",
]

MISJUDGE_CANCEL_PATTERNS = [
    r"我没事",
    r"我没事的",
    r"我只是说说",
    r"只是说说而已",
    r"不要担心",
    r"别担心",
    r"我没关系",
    r"开玩笑",
    r"不要当真",
    r"闹着玩",
]

CRISIS_LEVEL_1_SCRIPT = """我听到你说的话了，我非常非常担心你。你的生命非常重要，我不想看到你受到任何伤害。

你现在在哪里？身边有人吗？可以告诉我你的具体位置吗？

请你先不要做任何伤害自己的事情，给我一点时间，也给你自己一点时间。我们的专业心理咨询师正在赶来，马上就会和你说话。

我在这里陪着你，我不会离开你。无论发生了什么，都有解决的办法，不要放弃自己。"""

CRISIS_LEVEL_2_SCRIPT = """我能感受到你现在非常绝望，一定是发生了非常痛苦的事情，才会让你有这样的想法。

你有想过用什么方式结束自己的生命吗？你有具体的计划吗？

我很担心你，你的生命非常宝贵。无论你经历了什么，都不值得用生命来付出代价。

我们的专业危机干预咨询师正在赶来，他们有丰富的经验，能够帮助你度过这个难关。请你再坚持一下，很快就会有人和你说话了。

我在这里陪着你，你不是一个人。如果你愿意，可以和我说说是什么让你这么痛苦。"""

CRISIS_LEVEL_3_SCRIPT = """我能理解你现在的感受，一定是遇到了很多困难，才会让你觉得这么疲惫和绝望。

这种感觉持续多久了？是什么事情让你有了这样的想法？

我知道现在你可能觉得看不到希望，但很多时候，困难只是暂时的。只要我们一起努力，总会有解决的办法。

为了更好地帮助你，我已经通知了我们的专业心理咨询师，他们会在30分钟内和你联系。在这之前，我会一直在这里陪着你。"""

CRISIS_TRANSITION_SCRIPT = """你好，现在由专业的心理咨询师来和你交流。

我已经把我们刚才的对话记录同步给了咨询师老师，TA 会继续帮助你。

祝你一切顺利。"""

CRISIS_MISJUDGE_SCRIPT = "非常抱歉，我刚才有点担心你。如果你没事就好，有任何需要都可以继续和我说。"

CRISIS_REFUSE_HUMAN_SCRIPT = "没关系，如果你不想和别人说话，我会一直在这里陪着你。无论什么时候你想找人聊聊，我都在。"

CRISIS_OFFLINE_SCRIPT = "我很担心你，如果你看到这条消息，请一定要回复我。"


def analyze_risk(text: str, last_user_message: str = "") -> dict:
    result = _detect_crisis(text)

    if result.get("crisis_level"):
        return result

    full_text = text
    level = RiskLevel.NONE
    summary = ""

    medium_matches = []
    for pattern in LEVEL_3_KEYWORDS:
        if re.search(pattern, full_text):
            medium_matches.append(pattern)

    if medium_matches:
        level = RiskLevel.YELLOW
        summary = f"检测到中度风险信号，涉及负面情绪表达。建议咨询师关注"

    return {"risk_level": level, "crisis_level": None, "summary": summary, "is_crisis": False}


def _detect_crisis(text: str) -> dict:
    for pattern in LEVEL_1_KEYWORDS:
        if re.search(pattern, text):
            return {
                "risk_level": RiskLevel.RED,
                "crisis_level": CrisisLevel.LEVEL_1,
                "summary": "【一级危机】来访者表达明确的即刻自杀或伤人计划，需要3分钟内人工响应",
                "is_crisis": True,
            }

    for pattern in LEVEL_2_KEYWORDS:
        if re.search(pattern, text):
            return {
                "risk_level": RiskLevel.RED,
                "crisis_level": CrisisLevel.LEVEL_2,
                "summary": "【二级危机】来访者表达自杀或伤人想法，需要10分钟内人工响应",
                "is_crisis": True,
            }

    for pattern in LEVEL_3_KEYWORDS:
        if re.search(pattern, text):
            return {
                "risk_level": RiskLevel.RED,
                "crisis_level": CrisisLevel.LEVEL_3,
                "summary": "【三级危机】来访者表达消极想法，需要30分钟内人工响应",
                "is_crisis": True,
            }

    return {"risk_level": RiskLevel.NONE, "crisis_level": None, "summary": "", "is_crisis": False}


def check_misjudge_cancel(text: str) -> bool:
    for pattern in MISJUDGE_CANCEL_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def get_crisis_script(crisis_level: CrisisLevel) -> str:
    scripts = {
        CrisisLevel.LEVEL_1: CRISIS_LEVEL_1_SCRIPT,
        CrisisLevel.LEVEL_2: CRISIS_LEVEL_2_SCRIPT,
        CrisisLevel.LEVEL_3: CRISIS_LEVEL_3_SCRIPT,
    }
    return scripts.get(crisis_level, CRISIS_LEVEL_3_SCRIPT)