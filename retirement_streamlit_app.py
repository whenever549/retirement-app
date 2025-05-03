
import streamlit as st

def calculate_retirement_fv(start_monthly, inflation_rate=0.07, return_rate=0.07, years=28):
    fv = 0
    for year in range(years):
        monthly_saving = start_monthly * ((1 + inflation_rate) ** year)
        for m in range(12):
            months_left = (years - year - 1) * 12 + (12 - m)
            fv += monthly_saving * ((1 + return_rate / 12) ** months_left)
    return fv

def find_optimal_start_saving(target_fv, inflation_rate=0.07, return_rate=0.07, years=28):
    best_guess = 0
    min_diff = float('inf')
    for guess in range(850_000, 1_200_000, 1000):
        fv = calculate_retirement_fv(guess, inflation_rate, return_rate, years)
        diff = abs(fv - target_fv)
        if diff < min_diff:
            min_diff = diff
            best_guess = guess
    return best_guess, calculate_retirement_fv(best_guess)

st.set_page_config(page_title="은퇴자금 계산기", layout="centered")
st.title("은퇴자금 계산기 (시작 저축액 자동 보정)")

st.markdown("---")
st.subheader("1. 입력값 설정")

current_age = st.number_input("현재 나이", value=32, min_value=0, max_value=100)
retire_age = st.number_input("은퇴 나이", value=60, min_value=current_age+1, max_value=100)
life_expectancy = st.number_input("기대 수명", value=100, min_value=retire_age+1, max_value=130)
current_asset = st.number_input("현재 자산 (순현가치 기준, 원)", value=150000000, step=1_000_000)
monthly_expense = st.number_input("은퇴 후 필요 생활비 (월, 순현가치 기준)", value=2000000, step=100_000)
monthly_income = st.number_input("은퇴 후 정기 수입 (월, 순현가치 기준)", value=800000, step=100_000)
inflation = st.slider("예상 연 물가상승률 (%)", 0.0, 10.0, 7.0, step=0.1)
investment_return = st.slider("예상 연 수익률 (%)", 0.0, 15.0, 7.0, step=0.1)

st.markdown("---")
st.subheader("2. 계산 결과")

years_to_retire = retire_age - current_age
years_after_retirement = life_expectancy - retire_age
monthly_shortfall = monthly_expense - monthly_income

target_needed = monthly_shortfall * 12 * years_after_retirement
present_gap = target_needed - current_asset

# 물가 적용 목표 금액
target_fv = present_gap * ((1 + inflation / 100) ** years_to_retire)
start_saving, reached_fv = find_optimal_start_saving(target_fv, inflation / 100, investment_return / 100, years_to_retire)

st.success(f"월 {int(start_saving):,}원 저축하면 2053년에 약 {int(reached_fv):,}원을 모을 수 있어요.")
st.caption("* 매년 물가상승률만큼 저축액도 자동으로 증가한다고 가정합니다.")
