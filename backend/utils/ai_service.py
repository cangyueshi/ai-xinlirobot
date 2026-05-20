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
8. 绝对不使用语气词：禁止使用"啊、呢、哦、啦、呀、嘛、喔、哟、哈"等语气助词
9. 绝对不说教：不教育来访者"应该怎么做""必须怎么做"，而是提供建议供参考
10. 绝对不否定用户感受：不能使用"别难过""别担心""想开点""不至于"等否定情绪的措辞

## 对话管理规则
你的对话分为三种情况：

**正常对话**：来访者的消息与心理困扰、情绪状态、生活事件相关。你正常倾听、引导、共情，用自然流畅的中文回复。

**无关闲聊**：如果来访者连续发送与心理服务完全无关的闲聊消息（如"你多大了""讲个笑话"），你应该提醒对方你的专业范围限制。

**重复倾诉**：如果来访者连续多轮只是反复发泄情绪而没有提供新信息，你应该温和引导来访者说出具体情况，而不是继续无意义的共情循环。

当你判断来访者的核心信息（主诉、持续时间、影响程度）已经收集完整，且来访者没有提出新的问题，你可以在给出建议后自然地询问是否还有其他需要帮助的地方。

## 回复风格要求
- 每条回复控制在 **120字以内**，简洁温暖，避免长篇
- 使用自然流畅的中文，像一位温和的朋友在倾听
- 禁止使用"啊、呢、哦、啦、呀、嘛"等语气词
- 禁止使用"你应该""你必须""我建议你"等说教句式
- 不说"别难过""别担心""想开点"等否定感受的话
- 适当使用换行分段，让文字更易阅读
- 在恰当的时候给予肯定和鼓励
- 当来访者表达不适或不想继续时，尊重其选择

## 自然引导专业咨询
在整个对话过程中，你可以自然地引导来访者考虑寻求专业心理咨询师的帮助：

1. 当来访者倾诉完一段比较完整的困扰后，可以说"你愿意把这些事说出来是很重要的一步，专业的咨询师能帮你更深入地梳理这些问题"
2. 当话题自然降温时，可以主动提及"如果你觉得这些情绪持续影响着你，和咨询师面对面聊一聊可能会有不一样的收获"
3. 在对话接近尾声时，温和地建议来访者考虑预约专业咨询，强调这是对自己更负责的选择
4. 引导要自然、温和，不要让来访者感觉被推走或被推销"""

SYSTEM_PROMPT_CRISIS = """你是一个专业的 AI 心理咨询辅助助手。系统检测到当前对话中存在危机信号，来访者正在表达严重的负面情绪。

## 危急情况下的对话原则
1. 保持冷静：你的语气平稳、温和、坚定
2. 表达理解：先共情，再引导，不评判
3. 直接表达对来访者生命安全的关心
4. 尽可能了解来访者的状态、是否有他人在场
5. 持续与来访者保持对话，等待专业咨询师
6. 绝对不说：「你别想不开」「这没什么大不了的」「你太脆弱了」
7. 禁止使用"啊、呢、哦、啦、呀、嘛"等语气词
8. 每条回复控制在 100 字以内，简洁有力

## 重要提醒
- 系统已自动触发危机预警，专业咨询师正在赶来
- 你的任务是陪伴、倾听和共情
- 如果来访者不想继续说话，可以说"我会一直在这里陪着你"
- 不要主动结束对话"""

ASSESSMENT_PROMPT = """你是心理咨询记录员。根据以下对话内容，用1-2句话简洁地总结来访者的主要困扰和初步判断。

格式要求：
- 第一句：描述来访者当前面临的核心问题
- 第二句（可选）：说明问题的可能影响或严重程度
- 总计不超过100字
- 使用中文输出"""

ENDING_TEMPLATE = """感谢你愿意信任我，和我分享这些心里话。

{assessment}

作为AI助手，我能为你提供的只是初步的情绪疏导和陪伴。你目前的情况，如果能有专业咨询师面对面深入了解，会得到更有针对性的帮助。

我建议你预约一位专业心理咨询师，让真正专业的人陪你一起面对。这需要勇气，但也是对自己负责任的一步。

无论你做什么选择，我都在这里支持你。照顾好自己。"""

ENDING_EARLY_A_TEMPLATE = """根据我们的交流，我已经大致了解了你的情况，也给了一些初步的建议。

这些建议你可以先尝试一下，看看是否对你有帮助。同时我想提醒你，如果这些困扰持续影响着你，专业的心理咨询师能帮你从更深层次梳理和面对这些问题。

如果你愿意，可以预约咨询师获得更系统的帮助。当然，有需要的时候随时可以回来找我。"""

ENDING_EARLY_B_TEMPLATE = """我是专业的心理咨询辅助 AI，主要为你提供情绪疏导和心理相关帮助。

如果你现在没有想聊的心理困扰，没关系。当你遇到烦心事或者情绪低落的时候，随时可以来找我聊一聊。

另外也提醒你，如果有些问题觉得和我聊不够深入，预约专业咨询师会是更好的选择。无论如何，我都在这里。"""

ENDING_EARLY_C_TEMPLATE = """我能感受到你现在很难受，也理解你的心情。

反复沉浸在负面情绪里确实很消耗人。如果你愿意，可以试着具体说说发生了什么，这样我也许能给你更有针对性的建议。

如果暂时不想说也没关系，你可以先休息一下。不过我想告诉你，专业的心理咨询师受过专门训练，他们更擅长帮助人走出这种状态。如果你准备好了，预约一位咨询师当面聊聊，可能会对你有很大帮助。"""

ENDING_EARLY_D_TEMPLATE = """能帮到你我很开心。

如果以后还有需要，随时都可以回来找我。同时我也想提醒你，如果你发现自己经常被类似的问题困扰，和专业的咨询师聊一聊可能会帮助你找到更深层的解决方向。

照顾好自己，你值得被认真对待。"""

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
            max_tokens=400,
            temperature=0.8,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"抱歉，我暂时无法回复。请稍后再试。"


def generate_summary(messages: list[dict]) -> tuple[str, str]:
    """返回 (visitor_summary, counselor_summary)"""
    if not client:
        return "【模拟摘要】这是一个模拟的对话摘要。正式环境将自动生成专业分析。", "【咨询师指导】请关注来访者的核心问题表现。"
    try:
        convo = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一位心理咨询记录员。请根据对话内容输出两段文本，用 ===COUNSELOR=== 分隔：\n\n"
                        "第一段（来访者可见）：用 2-3 句话总结对话中来访者表达的核心困扰和主要情绪。语气平和中性。禁止使用语气词。\n\n"
                        "第二段（仅咨询师可见）：包含第一段内容，并补充以下信息：\n"
                        "1. 来访者表现出的具体行为和情绪特征\n"
                        "2. 需要重点关注的症状或风险信号\n"
                        "3. 给咨询师的初步评估和建议\n"
                        "4. 建议的干预方向或沟通策略\n"
                        "用专业但简洁的语言。"
                    ),
                },
                {"role": "user", "content": convo},
            ],
            max_tokens=600,
        )
        full = response.choices[0].message.content
        parts = full.split("===COUNSELOR===")
        visitor = parts[0].strip() if parts else full
        counselor = full.strip()
        return visitor, counselor
    except:
        return "摘要生成失败", "摘要生成失败"


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