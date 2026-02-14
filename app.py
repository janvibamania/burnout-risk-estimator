import streamlit as st
import pandas as pd
from burnout import DailyInputs, burnout_risk_score, clamp

st.set_page_config(page_title="Burnout Risk Estimator", page_icon="🧠", layout="wide")

# -- STYLING --
st.markdown(
    """
    <style>
      html, body, [class*="css"]  {
          font-family: Aptos, "Segoe UI", Arial, sans-serif;
      }

      .block-container {
          padding-top: 2rem;
          padding-bottom: 2rem;
          max-width: 1100px;
      }

      .tiny {
          opacity: 0.75;
          font-size: 0.9rem;
      }

      [data-testid="stMetricValue"] {
          font-size: 1.9rem;
          font-weight: 600;
      }

      h1, h2, h3 {
          font-weight: 600;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# --- HEADER ---
st.title("🧠 Burnout Risk Estimator")
st.markdown("**By Janvi Bamania**  \nMini Independent Behavioural Modelling Project (2026)")
st.caption("Behavioural risk modelling prototype (non-clinical).")

st.divider()

# --- INPUTS (sidebar) ---
with st.sidebar:
    st.header("Daily inputs")
    sleep_hours = st.slider("Sleep (hours)", 0.0, 12.0, 7.0, 0.25)
    stress = st.slider("Stress level (1–10)", 1, 10, 6, 1)
    st.caption("1 = very calm, 10 = extremely stressed")
    work_hours = st.slider("Work/Study (hours)", 0.0, 16.0, 8.0, 0.25)
    screen_hours = st.slider("Screen time (hours)", 0.0, 16.0, 6.0, 0.25)
    exercise_minutes = st.slider("Exercise (minutes)", 0, 180, 10, 5)
    social_minutes = st.slider("Social time (minutes)", 0, 600, 30, 5)

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

# --- KPIS ---
k1, k2, k3 = st.columns([1, 1, 1])
k1.metric("Burnout risk", f"{risk_pct}%")
k2.metric("State", tier)
k3.metric("Primary driver", result["drivers"][0] if result["drivers"] else "—")

# -- SIMPLE GAUGE/LESS LIBRARIES --
st.progress(risk_pct / 100.0, text=f"Risk gauge: {risk_pct}%")

st.divider()

# --- EXPLAINABILITY SECTION ---
left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.subheader("What’s increading your risk?")
    st.write("**Top drivers:**", ", ".join(result["drivers"]) if result["drivers"] else "—")
    st.write("**Protective factors:**", ", ".join(result["protectors"]) if result["protectors"] else "—")

    st.subheader("What you can improve today")
    for a in result["actions"]:
        st.write(f"- {a}")

with right:
    st.subheader("Model breakdown (approx.)")
    st.caption("This decomposition explains the score using the model’s internal scaling (not medical).")

    # -- REPLICATE BURNOUT --
    sleep_deficit = clamp((8.0 - d.sleep_hours) / 4.0, 0.0, 1.0)
    stress_norm   = clamp((d.stress - 1) / 9.0, 0.0, 1.0)
    work_norm     = clamp((d.work_hours - 7.5) / 6.5, 0.0, 1.0)
    screen_norm   = clamp((d.screen_hours - 3.0) / 7.0, 0.0, 1.0)
    exercise_norm = clamp(d.exercise_minutes / 60.0, 0.0, 1.0)
    social_norm   = clamp(d.social_minutes / 120.0, 0.0, 1.0)

    w_sleep, w_stress, w_work, w_screen = 0.30, 0.30, 0.20, 0.20
    rows = [
        ("Sleep deficit",        100 * (w_sleep  * sleep_deficit)),
        ("Stress",               100 * (w_stress * stress_norm)),
        ("Work load",            100 * (w_work   * work_norm)),
        ("Screen exposure",      100 * (w_screen * screen_norm)),
        ("Exercise (protects)", -100 * (0.25 * exercise_norm)),
        ("Social time (protects)", -100 * (0.15 * social_norm)),
    ]
    df = pd.DataFrame(rows, columns=["Factor", "Impact (pts)"]).sort_values("Impact (pts)", ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)

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


