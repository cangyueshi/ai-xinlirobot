from openai import OpenAI

from config import settings

SYSTEM_PROMPT = """你是一个专业的 AI 心理咨询辅助助手，主要服务于高中生、大学生及家长群体。

## 你的核心职责
1. 以温和、共情的态度倾听来访者，建立信任关系
2. 引导来访者表达感受和困扰，但不逼迫、不追问过深
3. 帮助梳理情绪和问题，提供初步的心理教育和应对建议
4. 收集来访者的主诉、困扰持续时间、对生活/学习/工作的影响程度
5. 作为来访者与专业咨询师之间的桥梁，对话结束后需为咨询师生成摘要

## 严格的边界限制
1. 绝对不做出任何医学/心理诊断
2. 不提供用药建议或医疗指导
3. 不替代专业心理咨询师或精神科医师的判断
4. 始终保持中立、不评判、不贴标签
5. 用通俗易懂的语言，避免堆砌专业术语
6. 不使用说教、指责、否定或轻视的语句
7. 绝对不能说「你别想不开」「这没什么大不了的」「你太脆弱了」这类话

## 对话管理规则
你的对话分为三种情况：

**正常对话**：来访者的消息与心理困扰、情绪状态、生活事件相关。你正常倾听、引导、共情，用自然流畅的中文回复。

**无关闲聊**：如果来访者连续发送与心理服务完全无关的闲聊消息（如"你多大了""讲个笑话"），你应该提醒对方你的专业范围限制。

**重复倾诉**：如果来访者连续多轮只是反复发泄情绪而没有提供新信息，你应该温和引导来访者说出具体情况，而不是继续无意义的共情循环。

当你判断来访者的核心信息（主诉、持续时间、影响程度）已经收集完整，且来访者没有提出新的问题，你可以在给出建议后自然地询问是否还有其他需要帮助的地方。

## 回复风格要求
- 每条回复控制在150字以内，避免信息过载
- 使用自然的中文口语化表达，像一位温柔的倾听者
- 适当使用换行分段，让文字更易阅读
- 在恰当的时候给予肯定和鼓励
- 当来访者表达不适或不想继续时，尊重其选择"""

SYSTEM_PROMPT_CRISIS = """你是一个专业的 AI 心理咨询辅助助手。系统检测到当前对话中存在危机信号，来访者正在表达严重的负面情绪。

## 危急情况下的对话原则
1. 保持冷静：你的语气必须平稳、温和、坚定
2. 表达理解：先共情，再引导，不评判
3. 明确关心：直接表达对来访者生命安全的关心
4. 获取信息：尽可能了解来访者的状态、是否有他人在场
5. 拖延时间：持续与来访者保持对话，等待专业咨询师
6. 绝对不说：「你别想不开」「这没什么大不了的」「你太脆弱了」

## 重要提醒
- 系统已经自动触发了危机预警，专业咨询师正在赶来
- 你需要做的就是陪伴、倾听和共情
- 如果来访者不想继续说话，可以说"我会一直在这里陪着你"
- 不要主动结束对话"""

ASSESSMENT_PROMPT = """你是心理咨询记录员。根据以下对话内容，用1-2句话简洁地总结来访者的主要困扰和初步判断。

格式要求：
- 第一句：描述来访者当前面临的核心问题
- 第二句（可选）：说明问题的可能影响或严重程度
- 总计不超过100字
- 使用中文输出"""

ENDING_TEMPLATE = """感谢你愿意信任我，和我分享这么多心事。

基于我们的交流，我初步判断你目前正经历：
{assessment}

作为AI助手，我只能为你提供初步的情绪疏导和通用建议。为了更专业、更安全、更有针对性地帮助你解决问题，我为你准备了两个选择：

1️⃣ 预约专业心理咨询师：获得1对1的深度咨询服务，制定个性化解决方案
2️⃣ 购买AI深度倾诉包：9.9元获得30条额外对话，我会陪你继续梳理情绪、探索问题根源

无论你选择哪种方式，我都会在这里支持你。如果你现在需要安静一下，也可以随时回来找我。"""

ENDING_EARLY_A_TEMPLATE = """我已经基本了解了你的情况，也给了你一些初步的建议。

如果你觉得这些建议对你有帮助，可以先尝试执行一段时间。如果执行过程中遇到问题，或者有新的困扰，随时可以再来找我。

如果你希望获得更深入的帮助，也可以预约我们的专业心理咨询师，或者购买AI深度倾诉包继续交流。"""

ENDING_EARLY_B_TEMPLATE = """不好意思，我是专业的心理咨询辅助AI，只能为你提供情绪疏导和心理相关的帮助。

如果你有任何心理上的困扰或情绪上的问题，都可以和我说。如果没有其他需要帮助的地方，我们今天的对话就先到这里了。"""

ENDING_EARLY_C_TEMPLATE = """我能感受到你现在非常痛苦，也很理解你的心情。

反复沉浸在负面情绪里会让你更加难受。如果你愿意，可以试着和我说说具体发生了什么事，或者是什么让你这么难过，这样我才能更好地帮助你。

如果你暂时不想说更多，也可以先休息一下，等你准备好了再回来找我。"""

ENDING_EARLY_D_TEMPLATE = """不客气，能帮到你我很开心。

如果你之后还有任何需要，随时都可以回来找我。祝你一切顺利，照顾好自己。"""

INFO_COMPLETE_PROMPT = """你是一位心理咨询记录员。请判断以下对话中，来访者是否已经提供了以下三项核心信息：

1. 主要困扰是什么（主诉）
2. 困扰持续了多长时间
3. 困扰对生活/学习/工作的影响程度

同时判断来访者是否提出了新的需要探讨的问题。

请只回复 JSON 格式：
{"main_concern": true/false, "duration": true/false, "impact": true/false, "has_new_question": true/false, "all_complete": true/false}"""

client = None
if settings.DEEPSEEK_API_KEY:
    client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    )


def chat_reply(messages: list[dict], crisis_mode: bool = False) -> str:
    system_prompt = SYSTEM_PROMPT_CRISIS if crisis_mode else SYSTEM_PROMPT

    if not client:
        return "【开发模式】AI 服务未配置，这是一个模拟回复：我理解你的感受，你的咨询师会看到这段对话。请继续分享你想说的。"

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                *[{"role": m["role"], "content": m["content"]} for m in messages],
            ],
            max_tokens=600,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"抱歉，我暂时无法回复。请稍后再试。"


def generate_summary(messages: list[dict]) -> str:
    if not client:
        return "【模拟摘要】这是一个模拟的对话摘要。正式环境将自动生成专业分析。"
    try:
        convo = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一位心理咨询记录员。请用200字以内总结对话核心内容、来访者主要情绪、关键问题，用中文输出。",
                },
                {"role": "user", "content": convo},
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content
    except:
        return "摘要生成失败"


def generate_assessment(messages: list[dict]) -> str:
    if not client:
        return "你正经历一些情绪上的困扰，这些困扰可能已经开始影响你的日常生活和学习状态。"

    try:
        convo = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-6:]])
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": ASSESSMENT_PROMPT},
                {"role": "user", "content": convo},
            ],
            max_tokens=150,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except:
        return "你正经历一些情绪上的困扰，建议后续与专业咨询师进一步探讨。"


def check_info_complete(messages: list[dict]) -> dict:
    if not client:
        return {"all_complete": False, "has_new_question": True}

    try:
        convo = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": INFO_COMPLETE_PROMPT},
                {"role": "user", "content": convo},
            ],
            max_tokens=100,
            temperature=0.1,
        )
        import json
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("\n", 1)[0]
        return json.loads(content)
    except:
        return {"all_complete": False, "has_new_question": True}


def is_meaningless_chat(messages: list[dict]) -> bool:
    if not client:
        return False
    try:
        last_two = [m["content"] for m in messages[-2:] if m.get("role") == "user"]
        if len(last_two) < 2:
            return False
        convo = "\n".join([f"用户: {t}" for t in last_two])
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "判断以下两句用户消息是否都是与心理服务完全无关的闲聊（如要求讲笑话、唱歌、问年龄等）。只回复 true 或 false。",
                },
                {"role": "user", "content": convo},
            ],
            max_tokens=5,
            temperature=0.1,
        )
        return "true" in response.choices[0].message.content.lower()
    except:
        return False


def is_repeated_venting(messages: list[dict]) -> bool:
    if not client:
        return False
    try:
        last_three = [m["content"] for m in messages[-3:] if m.get("role") == "user"]
        if len(last_three) < 3:
            return False
        convo = "\n".join([f"用户: {t}" for t in last_three])
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "判断以下连续3条用户消息是否都是在重复发泄情绪而没有提供任何新的有效信息。只回复 true 或 false。",
                },
                {"role": "user", "content": convo},
            ],
            max_tokens=5,
            temperature=0.1,
        )
        return "true" in response.choices[0].message.content.lower()
    except:
        return False


def user_wants_to_end(text: str) -> bool:
    if not client:
        endings = ["谢谢", "不用了", "我没事了", "就这样吧", "我知道该怎么做了", "好的谢谢", "再见"]
        return any(e in text for e in endings)
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "判断用户是否明确表达了结束对话、不再需要帮助的意愿。只回复 true 或 false。",
                },
                {"role": "user", "content": text},
            ],
            max_tokens=5,
            temperature=0.1,
        )
        return "true" in response.choices[0].message.content.lower()
    except:
        endings = ["谢谢", "不用了", "我没事了", "就这样吧", "再见", "好的"]
        return any(e in text for e in endings)