import asyncio
import ssl
import time
import urllib
import uuid
from datetime import datetime
import aiohttp
import certifi
import jwt
from manager.webhook_manager import send_webhook


async def order(ACCESS_KEY, SECRET_KEY, coin, type, volume):
    """
    Upbit 시장가 주문 함수.

    매개변수:
      - ACCESS_KEY: Upbit API Access Key
      - SECRET_KEY: Upbit API Secret Key
      - type: 주문 타입 ("bid"이면 매수, "ask"이면 매도)
      - volume: 주문 금액(매수 시) 또는 코인 수량(매도 시)

    리턴:
      - API 응답 JSON (dict)
    """
    # Upbit 주문 API 엔드포인트
    url = "https://api.upbit.com/v1/orders"
    # nonce 생성 (고유값)
    nonce = str(uuid.uuid4())
    # 거래할 마켓 (필요에 따라 변경)
    market = coin

    # 주문 파라미터 설정 (주문 종류에 따라 price 혹은 volume 사용)
    if type == "bid":
        # 매수(시장가) 주문: 'price' 파라미터에 주문 금액을 지정
        data = {
            "market": market,
            "side": "bid",
            "price": str(volume),  # 주문 금액 (원화)
            "ord_type": "price"  # 시장가 매수 주문은 ord_type이 "price"
        }
    elif type == "ask":
        # 매도(시장가) 주문: 'volume' 파라미터에 주문 수량을 지정
        data = {
            "market": market,
            "side": "ask",
            "volume": str(volume),  # 주문 코인 수량
            "ord_type": "market"  # 시장가 매도 주문은 ord_type이 "market"
        }
    else:
        raise ValueError("유효하지 않은 주문 타입입니다. 'bid' 또는 'ask'여야 합니다.")

    # JWT 페이로드에 필요한 값 설정 (쿼리 스트링 포함)
    payload = {
        "access_key": ACCESS_KEY,
        "nonce": nonce,
        "query": urllib.parse.urlencode(data)
    }

    # JWT 토큰 생성 (HS256 알고리즘 사용)
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    # ssl 적용
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    # aiohttp를 사용하여 비동기로 POST 요청 전송
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers, ssl=ssl_context) as response:
            # API 응답 JSON 반환
            return await response.json()


async def process_trade(ACCESS_KEY, SECRET_KEY, coin, trading_dict, indicators_dict,
                        active_trades, wallet_dict, trading_lock, active_lock):
    """
    개별 코인 거래를 처리하는 비동기 함수입니다.
    거래 완료 후 active_trades, trading_dict에서 해당 코인을 삭제합니다.
    avg_buy_price:
        매수 평균 가격
    balance:
        매수 수량
    duration:
        매수 제한 시간(단위 : 초, 초과시 거래 종료)
    purchase_volume:
        구매 금액
    err_flag:
        잔고부족, 시간 초과 등의 문제 발생 여부 flag
    """
    print(f"[{datetime.now()}] {coin} 거래 시작")
    start_time = time.time()

    duration = 60
    purchase_volume = 8_000
    err_flag = False

    # 거래 조건(T-1의 지표들보다 현재가가 1% 이상 높음) 부합 확인, 거래 요청, 제한 시간 초과시 거래 종료
    while True:
        if time.time() - start_time > duration:
            err_flag = True
            print(f"[{datetime.now()}] {coin} 매수 실패, {duration} 초 시간 초과")
            break

        if max(indicators_dict.get(coin)[5], indicators_dict.get(coin)[7]) * 1.01 < trading_dict[coin]:
            result = await order(ACCESS_KEY, SECRET_KEY, coin, "bid", purchase_volume)

            if "error" in result:
                err_flag = True
                print(f"[{datetime.now()}] {coin} 매수 실패, 서버 오류 메세지 수신")
            else:
                message = f"{coin} 매수 완료"
                print(f"[{datetime.now()}]" , message)
                asyncio.create_task(send_webhook(message))
            break
        await asyncio.sleep(1)

    # 에러가 발생하지 않은 경우 - 거래 정상 진행
    if not err_flag:

        # wallet_dict 에서 현재 코인의 매수 갯수와 평균가 가져오기
        while True:
            if coin in wallet_dict and wallet_dict[coin] is not None:
                coin_wallet_list = wallet_dict[coin]
                break
            await asyncio.sleep(0.5)

        avg_buy_price = coin_wallet_list[0]
        balance = coin_wallet_list[1]

        # 가격 모니터링, 매도 조건 부합 확인, 매도 요청
        while True:
            price = trading_dict.get(coin)  # 실시간 현재가 - 구조상 trading_dict 에 키값 coin 이 반드시 존재

            # 매도 조건 부합 확인시 매도
            if price < max(indicators_dict.get(coin)[5], indicators_dict.get(coin)[7]):
                await order(ACCESS_KEY, SECRET_KEY, coin, "ask", balance)
                print(f"[{datetime.now()}] {coin} 매도 완료")
                break

            # 매도 조건 미부합 시 1초 대기 후 재확인
            await asyncio.sleep(1)

    # 에러가 발생한 경우 - 코인 제거 (거래 실패), 거래 종료 후- 코인 제거 (거래 성공)
    # 락(lock) 얻은 후 공유 자원에서 해당 코인 제거
    async with trading_lock, active_lock:
        active_trades.discard(coin)
        trading_dict.pop(coin, None)
        print(f"[{datetime.now()}] {coin} 거래 종료. trading_dict, active_trades 에서 삭제됨.")


async def execute_trades(ACCESS_KEY, SECRET_KEY, trading_dict, active_trades, indicators_dict, wallet_dict
                         , trading_lock, active_lock):
    """
    trading_dict에 존재하는 코인에 대해 개별 비동기 거래를 실행합니다.
    이미 거래 중인 코인(active_trades에 포함된 코인)은 건너뛰며,
    거래가 완료되면 각 작업이 trading_dict에서 해당 코인을 삭제합니다.

    함수 동작 방식:
      1. trading_dict는 외부에서 1초마다 업데이트됩니다.
      2. trading_dict에 있는 코인에 대해 거래를 개별 비동기 작업(Task)으로 진행합니다.
      3. 각 작업은 완료되면 trading_dict에서 자신의 코인을 삭제합니다.
      4. 이후 trading_dict 업데이트 시, 삭제된 코인의 자리는 다시 채워져 추가 거래가 진행됩니다.
    """

    while True:
        # trading_dict는 매 1초마다 업데이트되므로, 그 시점의 거래 대상 코인 목록을 확인
        for coin in list(trading_dict.keys()):
            async with active_lock:
                # 거래중이 아닌, trading_dict에 존재하는 코인만 거래를 시작함
                if coin not in active_trades:
                    active_trades.add(coin)
                    asyncio.create_task(
                        process_trade(ACCESS_KEY, SECRET_KEY, coin, trading_dict, indicators_dict,
                                      active_trades, wallet_dict, trading_lock, active_lock)
                    )
        await asyncio.sleep(1)
