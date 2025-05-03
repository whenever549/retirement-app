
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(page_title="은퇴자금 계산기", layout="wide")

# 타이틀
st.title("은퇴자금 계산기 (시작 저축액 자동 보정)")

# 입력값 받기
st.header("1. 입력값 설정")

col1, col2 = st.columns(2)

with col1:
    current_age = st.number_input("현재 나이", min_value=0, max_value=100, value=32)
    retirement_age = st.number_input("은퇴 나이", min_value=0, max_value=100, value=60)
    life_expectancy = st.number_input("기대 수명", min_value=0, max_value=120, value=100)

with col2:
    current_assets = st.number_input("현재 자산 (순현가치 기준, 원)", value=150000000)
    retirement_expense = st.number_input("은퇴 후 필요 생활비 (월, 순현가치 기준)", value=2000000)
    retirement_income = st.number_input("은퇴 후 정기 수입 (월, 순현가치 기준)", value=800000)

col3, col4 = st.columns(2)

with col3:
    inflation_rate = st.slider("예상 연 물가상승률 (%)", 0.0, 10.0, 3.0, step=0.1)
with col4:
    investment_return = st.slider("예상 연 수익률 (%)", 0.0, 15.0, 5.0, step=0.1)

# 계산
st.header("2. 계산 결과")

years_to_retire = retirement_age - current_age
years_in_retirement = life_expectancy - retirement_age
monthly_gap = retirement_expense - retirement_income
total_required_np = monthly_gap * 12 * years_in_retirement
shortfall_np = total_required_np - current_assets

# 명목가치 환산 (복리로 물가 상승률 적용)
nominal_shortfall = shortfall_np * ((1 + inflation_rate / 100) ** years_to_retire)

# 미래 저축금 누적 계산
future_value_factor = sum([(1 + investment_return / 100) ** i for i in range(years_to_retire)])
monthly_saving = nominal_shortfall / future_value_factor / 12

st.success(f"월 {int(monthly_saving):,}원 저축하면 {retirement_age}세에 약 {int(nominal_shortfall):,}원을 모을 수 있어요.")

st.caption("매년 물가상승률만큼 저축액도 자동으로 증가한다고 가정합니다.")

# 시각화
st.subheader("3. 연도별 저축 계획 시각화")

years = np.arange(current_age, retirement_age)
savings = [monthly_saving * 12 * ((1 + investment_return / 100) ** i) for i in range(years_to_retire)]

fig, ax = plt.subplots()
ax.plot(years, savings, marker='o')
ax.set_title("연도별 누적 저축액 (명목가치 기준)")
ax.set_xlabel("나이")
ax.set_ylabel("누적 저축액 (원)")
ax.grid(True)
st.pyplot(fig)
