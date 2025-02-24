import sys
import certifi
import websockets
from datetime import datetime
import ssl

async def public_websocket_connect():
    """"
    업비트 websocket_public 용으로 사용할 웹소켓을 반환합니다.
    """
    url = "wss://api.upbit.com/websocket/v1"
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    try:
        websocket = await websockets.connect(url, ssl=ssl_context, compression="deflate")
        print(f"[{datetime.now()}] ✅ 웹소켓 연결 성공!")
        return websocket
    except Exception as e:
        print(f"[{datetime.now()}] ❌ 웹소켓 연결 실패: {e}")
        sys.exit(0)