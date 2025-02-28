import asyncio
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

# 공유 자원 (각 Task들이 사용하는 데이터)
indicators_dict = {}
target_dict = {}
trading_dict = {}
wallet_dict = {}
active_trades = set()


# 비동기 락 (각 공유 자원별로 생성)
target_lock = asyncio.Lock()
trading_lock = asyncio.Lock()
active_lock = asyncio.Lock()

# 업비트 API 키
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")

# 웹훅 주소
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# 개별 거래 구매 금액
PURCHASE_VOLUME = int(os.environ.get("PURCHASE_VOLUME"))