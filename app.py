import streamlit as st
import pandas as pd
from burnout import DailyInputs, burnout_risk_score, clamp

st.set_page_config(page_title="Burnout Risk Estimator", page_icon="🧠", layout="centered")

# -- STYLING --
st.markdown("""
<style>

/* --- Background --- */
.stApp {
  background: linear-gradient(180deg, #F4F1FF 0%, #ECE8FF 100%);
}

/* --- Title smaller + try keep on one line --- */
h1 {
  color: #1E2A47 !important;
  font-weight: 800 !important;
  font-size: 2.05rem !important;
  line-height: 1.08 !important;
  white-space: nowrap !important;      /* try keep one line */
}
@media (max-width: 430px) {
  h1 { 
    font-size: 1.65rem !important;
    white-space: normal !important;    /* allow wrap if truly needed */
  }
}

/* --- Headings --- */
h2, h3 {
  color: #1E2A47 !important;
  font-weight: 750 !important;
}

/* --- Body text --- */
p, label, span {
  color: #3E4463 !important;
}

/* --- Subtle “card” look for expander header --- */
div[data-testid="stExpander"] > details > summary {
  background: rgba(30, 42, 71, 0.06) !important;  /* slightly darker than bg */
  border-radius: 14px !important;
  padding: 10px 12px !important;
  border: 1px solid rgba(30, 42, 71, 0.08) !important;
}

/* --- Button slightly darker than background --- */
button[kind="primary"], button[kind="secondary"], .stButton>button {
  background: rgba(30, 42, 71, 0.07) !important;
  border: 1px solid rgba(30, 42, 71, 0.10) !important;
  color: #1E2A47 !important;
  border-radius: 12px !important;
  font-weight: 650 !important;
}

/* --- FORCE sliders to pink (BaseWeb + iOS stubbornness) --- */

/* track (unfilled) */
.stSlider [data-baseweb="slider"] div[role="presentation"] {
  background-color: #DDE0F3 !important;
}

/* filled part */
.stSlider [data-baseweb="slider"] div[role="presentation"] div {
  background: linear-gradient(90deg, #FF6EC7, #FF4FA3) !important;
}

/* thumb */
.stSlider [data-baseweb="slider"] div[role="slider"] {
  background-color: #FF4FA3 !important;
  border: 2px solid #FFFFFF !important;
  box-shadow: 0 0 0 4px rgba(255,79,163,0.18) !important;
}

/* value text above slider (optional: make it match) */
.stSlider [data-testid="stTickBarMin"], 
.stSlider [data-testid="stTickBarMax"],
.stSlider .stSliderValue {
  color: #1E2A47 !important;
}

/* --- Remove metric white boxes --- */
div[data-testid="metric-container"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

/* --- Keep ombre progress --- */
div[data-testid="stProgress"] > div > div {
  background: linear-gradient(90deg, #FF9ECF, #8EC5FC, #B388FF) !important;
}

/* Divider */
hr {
  border: 0;
  height: 1px;
  background: rgba(30, 42, 71, 0.12);
}

</style>
""", unsafe_allow_html=True)




# --- HEADER ---
st.title("🧠 Burnout Risk Estimator")
st.markdown("**By Janvi Bamania**  \nMini Independent Behavioural Modelling Project (2026)")
st.caption("Behavioural risk modelling prototype (non-clinical).")

st.divider()

# --- INPUTS (sidebar) ---
with st.expander("Enter your inputs"):
    with st.form("inputs_form"):
        sleep_hours = st.slider("Sleep (hours)", 0.0, 12.0, 7.0, 0.25)
        stress = st.slider("Stress level (1–10)", 1, 10, 6, 1)
        st.caption("1 = very calm, 10 = extremely stressed")

        work_hours = st.slider("Work/Study (hours)", 0.0, 16.0, 8.0, 0.25)
        screen_hours = st.slider("Screen time (hours)", 0.0, 16.0, 6.0, 0.25)
        exercise_minutes = st.slider("Exercise (minutes)", 0, 180, 10, 5)
        social_minutes = st.slider("Social time (minutes)", 0, 600, 30, 5)

        submitted = st.form_submit_button("Calculate")
        if not submitted:
           st.stop()


d = DailyInputs(
    sleep_hours=sleep_hours,
    stress=stress,
    work_hours=work_hours,
    screen_hours=screen_hours,
    exercise_minutes=exercise_minutes,
    social_minutes=social_minutes,
)

result = burnout_risk_score(d)
risk_pct = result["risk_pct"]

# --- TIERS ---
def tier_label(pct: int) -> str:
    if pct < 35:
        return "Stable"
    if pct < 65:
        return "Strained"
    return "Overload"

tier = tier_label(risk_pct)

# --- MOBILE METRICS ---
st.metric("Burnout risk", f"{risk_pct}%")
st.metric("State", tier)
st.metric("Primary driver", result["drivers"][0] if result["drivers"] else "—")


# -- SIMPLE GAUGE/LESS LIBRARIES --
st.markdown(f"""
<div style="
    height: 14px;
    width: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #f5c2d7, #8fb8d9, #c5b6e8);
    opacity: 0.25;
    margin-bottom: -14px;">
</div>

<div style="
    height: 14px;
    width: {risk_pct}%;
    border-radius: 10px;
    background: linear-gradient(90deg, #f5c2d7, #8fb8d9, #c5b6e8);
">
</div>

<p style="color:#6b7aa6; margin-top:6px;">
Risk gauge: {risk_pct}%
</p>
""", unsafe_allow_html=True)


st.divider()

# --- EXPLAINABILITY SECTION ---
left = st.container

st.subheader("What is increasing your risk?")

st.write("**Main drivers:**", ", ".join(result["drivers"]) if result["drivers"] else "—")
st.write("**Protective factors:**", ", ".join(result["protectors"]) if result["protectors"] else "—")

st.subheader("What you can improve today")

for a in result["actions"]:
    st.write(f"- {a}")
st.divider()


# --- RISK REDUCE ---
st.subheader("What change reduces risk fastest?")
st.caption("Try small changes to see what lowers your risk the most.")

base = risk_pct

def simulate(**kwargs) -> int:
    d2 = DailyInputs(
        sleep_hours=kwargs.get("sleep_hours", d.sleep_hours),
        stress=kwargs.get("stress", d.stress),
        work_hours=kwargs.get("work_hours", d.work_hours),
        screen_hours=kwargs.get("screen_hours", d.screen_hours),
        exercise_minutes=kwargs.get("exercise_minutes", d.exercise_minutes),
        social_minutes=kwargs.get("social_minutes", d.social_minutes),
    )
    return burnout_risk_score(d2)["risk_pct"]

c1, c2, c3 = st.columns(3)

sleep_plus = simulate(sleep_hours=min(12.0, d.sleep_hours + 1.0))
stress_minus = simulate(stress=max(1, d.stress - 2))
screen_minus = simulate(screen_hours=max(0.0, d.screen_hours - 1.0))

c1.metric("If +1h sleep", f"{sleep_plus}%", delta=f"{sleep_plus - base}%")
c2.metric("If -2 stress", f"{stress_minus}%", delta=f"{stress_minus - base}%")
c3.metric("If -1h screen", f"{screen_minus}%", delta=f"{screen_minus - base}%")

# -- CLOSING INSIGHT --
best = min(
    [("Sleep +1h", sleep_plus), ("Stress -2", stress_minus), ("Screen -1h", screen_minus)],
    key=lambda x: x[1]
)
st.markdown(
    f"**Biggest impact today:** {best[0]}. "
    "Small changes can quickly reduce pressure."
)

with st.expander("About this project"):
    st.write(
        "This is a small independent project that estimates burnout risk based on daily habits. "
        "It looks at things like sleep, stress, workload, screen time, exercise, and social time "
        "to give a simple risk score."
    )
    st.write(
        "It also shows which habits are increasing your risk the most and which small changes "
        "could lower it fastest."
    )
    st.write(
        "This tool is for personal insight only. It is not medical advice."
    )






















