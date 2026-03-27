import httpx
from app.config import get_settings

settings = get_settings()


async def send_email(to: str, subject: str, body_html: str) -> bool:
    if not settings.sendgrid_api_key:
        return False
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={"Authorization": f"Bearer {settings.sendgrid_api_key}"},
            json={
                "personalizations": [{"to": [{"email": to}]}],
                "from": {"email": "noreply@moadon-hasportaim.co.il", "name": "מועדון הספורטאים"},
                "subject": subject,
                "content": [{"type": "text/html", "value": body_html}],
            },
            timeout=10,
        )
    return resp.status_code == 202


async def send_whatsapp(phone: str, message: str) -> bool:
    if not settings.whatsapp_token or not settings.whatsapp_phone_number_id:
        return False
    url = f"https://graph.facebook.com/v19.0/{settings.whatsapp_phone_number_id}/messages"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            headers={"Authorization": f"Bearer {settings.whatsapp_token}"},
            json={
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": message},
            },
            timeout=10,
        )
    return resp.status_code == 200


async def send_push_notification(fcm_token: str, title: str, body: str) -> bool:
    if not settings.fcm_server_key:
        return False
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://fcm.googleapis.com/fcm/send",
            headers={
                "Authorization": f"key={settings.fcm_server_key}",
                "Content-Type": "application/json",
            },
            json={"to": fcm_token, "notification": {"title": title, "body": body}},
            timeout=10,
        )
    return resp.status_code == 200
