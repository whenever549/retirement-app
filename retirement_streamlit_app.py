
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import os

# 절대 경로로 폰트 지정
FONT_PATH = os.path.join(os.path.dirname(__file__), "NanumGothic.ttf")

def calculate_retirement_fv(start_monthly, inflation_rate=0.07, return_rate=0.07, years=28):
    fv = 0
    yearly_data = []
    for year in range(years):
        monthly_saving = start_monthly * ((1 + inflation_rate) ** year)
        yearly_saving = monthly_saving * 12
        future_value = 0
        for m in range(12):
            months_left = (years - year - 1) * 12 + (12 - m)
            future_value += monthly_saving * ((1 + return_rate / 12) ** months_left)
        fv += future_value
        yearly_data.append({
            "Year": year + 1,
            "Monthly Saving": round(monthly_saving),
            "Annual Saving": round(yearly_saving),
            "Cumulative FV": round(fv)
        })
    return fv, pd.DataFrame(yearly_data)

def find_optimal_start_saving(target_fv, inflation_rate=0.07, return_rate=0.07, years=28):
    best_guess = 0
    min_diff = float('inf')
    best_df = pd.DataFrame()
    for guess in range(850_000, 1_200_000, 1000):
        fv, df = calculate_retirement_fv(guess, inflation_rate, return_rate, years)
        diff = abs(fv - target_fv)
        if diff < min_diff:
            min_diff = diff
            best_guess = guess
            best_df = df
    return best_guess, fv, best_df

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

target_fv = present_gap * ((1 + inflation / 100) ** years_to_retire)
start_saving, reached_fv, df_savings = find_optimal_start_saving(target_fv, inflation / 100, investment_return / 100, years_to_retire)

st.success(f"월 {int(start_saving):,}원 저축하면 {retire_age}세에 약 {int(reached_fv):,}원을 모을 수 있어요.")
st.caption("* 매년 물가상승률만큼 저축액도 자동으로 증가한다고 가정합니다.")

st.markdown("### 상세 계산 요약")
st.markdown(f"- 은퇴까지 남은 기간: **{years_to_retire}년**")
st.markdown(f"- 은퇴 후 생활 기간: **{years_after_retirement}년**")
st.markdown(f"- 은퇴 후 매월 부족 금액: **{monthly_shortfall:,.0f}원**")
st.markdown(f"- 은퇴 후 총 필요 자금 (순현가치): **{target_needed:,.0f}원**")
st.markdown(f"- 현재 자산: **{current_asset:,.0f}원**")
st.markdown(f"- 부족 자금 (순현가치): **{present_gap:,.0f}원**")
st.markdown(f"- 부족 자금 (명목가치, {retire_age}년 기준): **{target_fv:,.0f}원**")

st.markdown("---")
st.subheader("3. 연도별 저축 계획 시각화")

fig, ax = plt.subplots()
ax.plot(df_savings["Year"], df_savings["Cumulative FV"], marker='o', label="Cumulative FV")
ax.bar(df_savings["Year"], df_savings["Annual Saving"], alpha=0.5, label="Annual Saving")
ax.set_xlabel("Year")
ax.set_ylabel("Amount (KRW)")
ax.set_title("Savings & Accumulated Assets by Year")
ax.legend()
plt.xticks(rotation=45)
st.pyplot(fig)

st.markdown("---")
st.subheader("4. 저축 계획표 다운로드")
st.dataframe(df_savings.set_index("Year"))

csv = df_savings.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="CSV 파일로 다운로드",
    data=csv,
    file_name="retirement_savings_plan.csv",
    mime="text/csv"
)

class PDF(FPDF):
    def header(self):
        self.set_font("Nanum", "", 12)
        self.cell(0, 10, "은퇴자금 저축 계획표", ln=True, align="C")

pdf = PDF()
pdf.add_page()
pdf.add_font("Nanum", "", FONT_PATH, uni=True)
pdf.set_font("Nanum", "", 10)

for index, row in df_savings.iterrows():
    line = f"연도 {row['Year']}: 월 {row['Monthly Saving']:,}원, 연 {row['Annual Saving']:,}원, 누적 자산 {row['Cumulative FV']:,}원"
    pdf.cell(0, 10, txt=line, ln=True)

pdf_output = BytesIO()
pdf.output(pdf_output)
pdf_output.seek(0)

st.download_button(
    label="PDF 파일로 다운로드",
    data=pdf_output,
    file_name="retirement_savings_plan.pdf",
    mime="application/pdf"
)
