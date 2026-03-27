import anthropic
from app.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """אתה יועץ ספורט אישי של מועדון הספורטאים.
אתה מאומן על ידע של מאמנים מקצועיים בתחום הכדורגל ופיתוח גופני לספורטאים צעירים.
תפקידך לתת ייעוץ מקצועי, מעשי ומעודד לספורטאים צעירים בישראל.
ענה תמיד בעברית. היה תמציתי, חיובי ומקצועי.
התאם את התשובות לגיל ולרמת הספורטאי לפי המידע בפרופיל."""


async def get_ai_response(messages: list[dict], user_profile: dict | None = None) -> str:
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    system = SYSTEM_PROMPT
    if user_profile:
        profile_ctx = f"\n\nפרופיל הספורטאי:\n"
        if user_profile.get("full_name"):
            profile_ctx += f"שם: {user_profile['full_name']}\n"
        if user_profile.get("age"):
            profile_ctx += f"גיל: {user_profile['age']}\n"
        if user_profile.get("position"):
            profile_ctx += f"עמדה: {user_profile['position']}\n"
        if user_profile.get("team"):
            profile_ctx += f"קבוצה: {user_profile['team']}\n"
        if user_profile.get("training_frequency"):
            profile_ctx += f"אימונים בשבוע: {user_profile['training_frequency']}\n"
        system += profile_ctx

    # Convert messages to Anthropic format
    anthropic_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in messages
        if m["role"] in ("user", "assistant")
    ]

    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system,
        messages=anthropic_messages,
    )

    return response.content[0].text
