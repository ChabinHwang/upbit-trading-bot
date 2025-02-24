import httpx
from upbit.shared_resources import WEBHOOK_URL

async def send_webhook(message):
    # 전송할 데이터
    payload = {
        'content': message
    }
    headers={
        "Content-Type": "application/json"
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(WEBHOOK_URL, json=payload, headers=headers)
    except Exception as e:
        print("웹훅 전송 중 오류 발생")