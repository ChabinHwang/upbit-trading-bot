# 🚀 매매 전략 - v1
📌 **코인 거래 봇 v1.x.x의 매매 전략 문서입니다.**

---

## 📊 **매매 전략 설명 (Trading Strategy)**
### ✨ **전략 개요**
✅ 분봉을 활용하여 **분 단위 판단 후 거래**를 진행함  
✅ **지표 활용:**  
   - 📌 `VWMA` (거래량 가중 이동평균선, 100)  
   - 📌 `MA` (이동평균선, 20)  
✅ **T-1과 T-2 시점의 지표 및 거래량 분석** 후 매매 결정

### 🎯 **거래 대상 코인 선정 조건**
🔍 **다음 조건을 모두 충족할 경우, 거래 대상 코인으로 선정!**  
1️⃣ **T-2 시점**  
   - `MA` 20과 `VWMA` 100이 **T-2 종가보다 낮아야 함**

2️⃣ **T-1 시점**  
   - `MA` 20과 `VWMA` 100이 **T-1 종가보다 낮아야 함**  

3️⃣ **거래량 조건**  
   - T-1의 거래량이 **T-2 거래량의 3배 이상**이어야 함


4️⃣ **현재가 조건**  
   - 현재가가 **T-1 종가보다 높아야 함**


5️⃣ **거래대금 조건**
   - `T-1 거래량` x `T-1 종가`가 `50_000_000`(5,000 만원) 보다 높아야 함

6️⃣ **모든 조건을 만족하면 target_dict에 추가!** ✅  

### 📈 **매수 조건**
🚀 **T-1 지표들보다 현재가가 1% 이상 높을 경우 매수**
⚠️ **제한 시간(60초) 초과 시, 거래 종료**

### 📉 **매도 조건**
🔻 **`T-1의 지표들 중 최대값` 보다 현재가가 낮아지면 즉시 시장가로 매도**<br>
🔻 **`구매 가격`보다 현재가가 3%이상 상승시 즉시 시장가로 매도**<br>
🔻 **`구매 가격`보다 현재가가 1%이상 하락시 즉시 시장가로 매도**<br>
🔻 **즉시 거래 종료**

---
### 📊 **매매 결과 - v1.3.1**
#### 📅 기간: 2월 27일 ~ 2월 28일
#### 📌 총 거래 횟수: 6회
**📉손실이 안나도 되는 거래에서 많이 나는것을 확인한 후, 판매 조건이 부실하다고 판단**

#### 📸 매매 결과

<img alt="Image" src="https://github.com/user-attachments/assets/fbb3a934-14f2-4187-aba4-66be58f59ac0" />

<img alt="Image" src=" https://github.com/user-attachments/assets/905a54a1-e4ec-4fe3-8694-cedbbc8b439c"/>



<details>
  <summary><b>📊매매 결과 - v1.1.0 (2/15~2/19)</b></summary>
  <p><strong>📅 기간:</strong> 2월 15일 ~ 2월 19일</p>
  <p><strong>📌 총 거래 횟수:</strong> 300회</p>
  <h3>📉 손실과 이익 퍼센테이지는 비슷했으나, 손실 횟수가 이익 횟수보다 많았음</h3>
  <p>📌 전략 수정 혹은 추가 조건 보완이 필요하다고 판단됨</p>
  <h3>📸 매매 결과 그래프</h3><br>
  <img alt="Image" src="https://github.com/user-attachments/assets/2ad5ceb9-4dd9-4395-9d3b-94c9ffa423f9" />
  <img alt="Image" src="https://github.com/user-attachments/assets/6461ff72-c750-45af-8276-69262a84743f" />
  <img alt="Image" src="https://github.com/user-attachments/assets/6b951d87-bc24-4f43-bec2-fd22c647f2f9" />
</details>

