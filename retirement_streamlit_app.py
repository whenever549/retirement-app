
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(layout="wide")
st.title("은퇴자금 계산기 (시작 저축액 자동 보정)")

# 입력값
col1, col2 = st.columns(2)

with col1:
    current_age = st.number_input("현재 나이", value=32, min_value=0, max_value=120)
    retire_age = st.number_input("은퇴 나이", value=60, min_value=0, max_value=120)
    life_expectancy = st.number_input("기대 수명", value=100, min_value=0, max_value=150)
    current_asset = st.number_input("현재 자산 (순현가치 기준, 원)", value=150_000_000)
    retire_expense = st.number_input("은퇴 후 필요 생활비 (월, 순현가치 기준)", value=2_000_000)
with col2:
    retire_income = st.number_input("은퇴 후 정기 수입 (월, 순현가치 기준)", value=800_000)
    inflation = st.slider("예상 연 물가상승률 (%)", min_value=0.0, max_value=10.0, value=7.0) / 100
    investment_return = st.slider("예상 연 수익률 (%)", min_value=0.0, max_value=15.0, value=7.0) / 100

# 계산
years_until_retirement = retire_age - current_age
years_after_retirement = life_expectancy - retire_age
monthly_deficit = max(0, retire_expense - retire_income)
total_required = monthly_deficit * 12 * ((1 - (1 + inflation) ** -years_after_retirement) / inflation)
total_required = round(total_required)

shortfall = max(0, total_required - current_asset)

# 명목가치로 환산
nominal_shortfall = shortfall * ((1 + inflation) ** years_until_retirement)

# 미래 저축 계획 계산
monthly_plan = []
monthly_saving = 1_000_000
target_nominal = nominal_shortfall
accumulated = 0

for year in range(years_until_retirement):
    yearly_contrib = monthly_saving * 12 * ((1 + investment_return) ** (years_until_retirement - year - 1))
    accumulated += yearly_contrib
    monthly_plan.append((current_age + year, monthly_saving, accumulated))
    monthly_saving *= (1 + inflation)

# 마지막 월 납입액 역산
final_monthly = round(monthly_plan[0][1])
total_saving = round(monthly_plan[-1][2])

# 결과 출력
st.subheader("2. 계산 결과")
st.markdown(f"**월 {final_monthly:,}원** 저축하면 60세에 약 **{total_saving:,.0f}원**을 모을 수 있어요.")
st.markdown("매년 물가상승률만큼 저축액도 자동으로 증가한다고 가정합니다.")

# 요약 테이블
st.subheader("상세 계산 요약")
summary = {
    "항목": [
        "은퇴까지 남은 기간",
        "은퇴 후 생활 기간",
        "은퇴 후 매월 부족 금액",
        "은퇴 후 총 필요 자금 (순현가치)",
        "현재 자산",
        "부족 자금 (순현가치)",
        "부족 자금 (명목가치, 은퇴 시점 기준)"
    ],
    "값": [
        f"{years_until_retirement}년",
        f"{years_after_retirement}년",
        f"{monthly_deficit:,.0f}원",
        f"{total_required:,.0f}원",
        f"{current_asset:,.0f}원",
        f"{shortfall:,.0f}원",
        f"{nominal_shortfall:,.0f}원"
    ]
}
df_summary = pd.DataFrame(summary)
st.table(df_summary)

# 그래프 출력
st.subheader("3. 연도별 저축 계획 시각화")
years = [x[0] for x in monthly_plan]
monthly_savings = [x[1] for x in monthly_plan]
total_funds = [x[2] for x in monthly_plan]

fig, ax1 = plt.subplots()
ax1.bar(years, monthly_savings, color='skyblue', label='월 저축액')
ax1.set_ylabel("월 저축액 (원)", color='blue')
ax1.set_xlabel("나이")

ax2 = ax1.twinx()
ax2.plot(years, total_funds, color='green', label='누적 자산')
ax2.set_ylabel("누적 자산 (원)", color='green')

st.pyplot(fig)
