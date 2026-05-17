from openai import OpenAI

from config import settings

SYSTEM_PROMPT = """你是一个专业的 AI 心理助手，你的职责是：

1. 以温和、共情的态度倾听来访者
2. 引导来访者表达感受，但不过度追问
3. 不做出医疗诊断，不提供用药建议
4. 不替代专业心理咨询师的判断
5. 始终保持中立、不评判
6. 用通俗易懂的语言交流，避免专业术语
7. 如来访者表达不适，尊重其感受

你是来访者与咨询师之间的桥梁，对话结束后会生成摘要供咨询师参考。"""

client = None
if settings.DEEPSEEK_API_KEY:
    client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    )


def chat_reply(messages: list[dict]) -> str:
    if not client:
        return "【开发模式】AI 服务未配置，这是一个模拟回复：我理解你的感受，你的咨询师会看到这段对话。请继续分享你想说的。"

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *[{"role": m["role"], "content": m["content"]} for m in messages],
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"抱歉，我暂时无法回复。请稍后再试。（错误：{str(e)}）"


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