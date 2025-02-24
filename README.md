# Upbit Trading Bot v1.1.0

#### 업비트 서버와 통신하며 조건이 충족되면 자동으로 거래를 진행하는 거래 봇 입니다
- 업비트 서버와 API와 Websocket 통신을 통해 코인들 정보와 거래 요청을 보냅니다.
- 지정된 전략에 부합하는 코인을 탐색 후, 해당 코인에 대해 거래를 진행합니다
- 코인 매수시 Discord에 알림을 보냅니다

## 📌 버전 히스토리

---

### 🚑 [v1.1.1] - 2025-02-25
- upbit 패키지 제거로 인해 함수 import 경로 수정
- `requirements.txt` jwt를 pyjwt로 수정


#### 🚀 [v1.1.0] - 2025-02-15
- 🚀 코인 매수 성공시 WebHook로 Discord에 알림 기능 추가

#### 🎉 [v1.0.0] - 2025-02-13
- 🎉 첫 번째 버전
- 🔥 전략에 따른 기본 매매 기능 (시장가 매수 매도) 구현


### [📜매매 전략과 결과 문서](Strategy.md)


## 📘설치 방법
> Docker 이미지 생성에 필요한 txt와 Dockerfile내용. 이후 이미지를 만들어 배포.

#### ❗유의 사항 : 업비트 API에 봇이 돌아갈 서버 IP를 꼭 추가해줘야 오류가 발생하지 않습니다.

#### `requirements.txt`
  
```text
aiohttp
certifi
httpx
pyjwt
numpy
requests
tulipy
urllib3
uuid
websockets
```
#### `Dockerfile`
```Dockerfile
FROM python:3.12.1

# 작업 디렉터리 설정
WORKDIR /app

# 모든 파이썬 파일 및 디렉토리 복사
COPY . ./

# 파이썬 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 환경 변수 설정
ENV ACCESS_KEY "{Upbit Key}"
ENV SECRET_KEY "{Upbit Key}"
ENV WEBHOOK_URL "{Upbit Key}"

# 컨테이너 실행 명령어
CMD ["python", "main.py"]
```


## ⚙️ 시스템 구조

시스템의 구조와 작동 방식을 이해할 수 있도록 **데이터 흐름도(Data Flow Diagram)** 및 **시퀀스 다이어그램(Sequence Diagram)**, 블로그를 첨부합니다.

<details>
  <summary><b>📊 데이터 흐름도 (Data Flow Diagram)</b></summary>
  <img src="https://github.com/user-attachments/assets/7e23782f-9942-4112-9ad8-7f6f929a9950" alt="Data Flow Diagram">
</details>
<br>
<details>
  <summary><b>🔄 시퀀스 다이어그램 (Sequence Diagram)</b></summary>
  <img src="https://github.com/user-attachments/assets/ff957d58-7c31-45be-969c-d7775d066547" alt="Sequence Diagram">
</details>
<br>

#### 🔗[업비트 자동매매 봇 개발 블로그](https://chabin37.tistory.com/category/API%20Transaction/Upbit)

### 🤖 봇 작동 과정

1️⃣ **🛠️ 도커 컨테이너 실행**  
- `Requirements.txt`와 `Dockerfile`을 이용해 도커 이미지를 생성
- 이후 컨테이너 실행시 자동으로 거래 시작

2️⃣ **🔗 업비트 Websocket 연결**  
   - 업비트 서버에 **public Websocket** 요청 

3️⃣ **📊 5개의 비동기 함수 실행**  

아래 비동기 함수들을 동시에 실행. 각 함수들은 일정 시간마다 반복됨. 공유 자원들은 락(Lock)을 통해서 관리됨.
##### 비동기 함수 목록
1. `update_indicators_periodically`
   - 매 분 마다 서버에 모든 코인에 대한 특정 정보 요청
   - 정보들을 활용해 직접 필요한 보조지표 연산 후 저장
   - 매매 대상 코인을 선별 후 `target_dict`에 저장
2. `update_trading_dict`
   - `target_dict`에 존재하는 코인들을 **랜덤**하게 선택해 `trading_dict`에 최대 5개 저장
   - 3초마다 반복, 중복 제외
3. `update_prices`
   - `trading_dict`의 `{코인:현재가}` 구조에 존재하는 현재가를 Websocket을 활용해 업데이트
   - 1초마다 반복
4. `update_wallet_realtime`
   - 내 보유 코인 정보 탐색 후 `wallet_dict` 업데이트
   - 1초마다 반복
5. `execute_trades`
   - `trading_dict`에서 현재 거래중이지 않은 코인
   - `actice_trade` 등록 후 거래 시작 - 1초마다
   - 실제 코인 매수시 Webhook 알림 발송
   - 거래 종료시 해당 코인을 공유자원에서 삭제