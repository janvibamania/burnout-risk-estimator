import streamlit as st
from burnout import DailyInputs, burnout_risk_score

st.set_page_config(page_title="Burnout Risk Estimator", page_icon="🧠")

st.title("🧠 Burnout Risk Estimator")
st.markdown("**By Janvi Bamania**  \nMini Independent Behavioural Modelling Project")
st.caption("Behavioural risk modelling prototype (non-clinical).")

st.sidebar.header("Daily Inputs")

sleep = st.sidebar.slider("Sleep (hours)", 0.0, 12.0, 7.0, 0.5)
stress = st.sidebar.slider("Stress (1–10)", 1, 10, 6)
work = st.sidebar.slider("Work/Study hours", 0.0, 16.0, 8.0, 0.5)
screen = st.sidebar.slider("Screen time (hours)", 0.0, 16.0, 6.0, 0.5)
exercise = st.sidebar.slider("Exercise (minutes)", 0, 180, 10)
social = st.sidebar.slider("Social time (minutes)", 0, 600, 30)

inputs = DailyInputs(
    sleep_hours=sleep,
    stress=stress,
    work_hours=work,
    screen_hours=screen,
    exercise_minutes=exercise,
    social_minutes=social
)

result = burnout_risk_score(inputs)

st.subheader("Risk Assessment")

col1, col2 = st.columns(2)

col1.metric("Burnout Risk", f"{result['risk_pct']}%")
col2.metric("Risk Tier", result["tier"])

st.divider()

st.subheader("Primary Drivers")
st.write(", ".join(result["drivers"]))

st.subheader("Protective Factors")
st.write(", ".join(result["protectors"]))

st.divider()

st.subheader("Recommended Actions")
for action in result["actions"]:
    st.write(f"- {action}")

st.caption("This tool demonstrates weighted behavioural modelling with explainable output.")
