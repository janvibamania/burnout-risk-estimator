from dataclasses import dataclass


@dataclass
class DailyInputs:
    sleep_hours: float
    stress: int
    work_hours: float
    screen_hours: float
    exercise_minutes: int
    social_minutes: int


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def burnout_risk_score(d: DailyInputs):
    """
    Returns:
        risk_pct (0–100),
        tier,
        drivers,
        protectors,
        actions
    """

    # --- Normalise inputs (0–1 scale) ---
    sleep_deficit = clamp((8 - d.sleep_hours) / 4, 0, 1)
    stress_norm = clamp((d.stress - 1) / 9, 0, 1)
    work_norm = clamp((d.work_hours - 7.5) / 6.5, 0, 1)
    screen_norm = clamp((d.screen_hours - 3) / 7, 0, 1)
    exercise_norm = clamp(d.exercise_minutes / 60, 0, 1)
    social_norm = clamp(d.social_minutes / 120, 0, 1)

    # --- Weights (risk contributors) ---
    w_sleep = 0.30
    w_stress = 0.30
    w_work = 0.20
    w_screen = 0.20

    risk_raw = (
        w_sleep * sleep_deficit +
        w_stress * stress_norm +
        w_work * work_norm +
        w_screen * screen_norm
    )

    # --- Protective factors ---
    protector_raw = (0.25 * exercise_norm) + (0.15 * social_norm)

    risk_adjusted = clamp(risk_raw - protector_raw, 0, 1)
    risk_pct = int(round(risk_adjusted * 100))

    # --- Tier logic ---
    if risk_pct < 35:
        tier = "Green"
    elif risk_pct < 65:
        tier = "Amber"
    else:
        tier = "Red"

    drivers = {
        "Sleep deficit": sleep_deficit,
        "Stress": stress_norm,
        "Workload": work_norm,
        "Screen exposure": screen_norm,
    }

    protectors = {
        "Exercise": exercise_norm,
        "Social time": social_norm,
    }

    top_drivers = sorted(drivers.items(), key=lambda x: x[1], reverse=True)[:2]
    top_protectors = sorted(protectors.items(), key=lambda x: x[1], reverse=True)[:2]

    # --- Smart suggestions ---
    actions = []

    if sleep_deficit > 0.5:
        actions.append("Increase sleep by 60–90 minutes tonight.")
    if stress_norm > 0.6:
        actions.append("Schedule a decompression block (10–15 min reset).")
    if work_norm > 0.6:
        actions.append("Set a hard stop time tomorrow.")
    if screen_norm > 0.6:
        actions.append("Add a 45-min screen-free period.")
    if exercise_norm < 0.3:
        actions.append("Add a 10-minute minimum movement session.")
    if social_norm < 0.2:
        actions.append("Reach out to one person today.")

    if not actions:
        actions = ["Maintain routine. Risk stable."]

    return {
        "risk_pct": risk_pct,
        "tier": tier,
        "drivers": [d[0] for d in top_drivers],
        "protectors": [p[0] for p in top_protectors],
        "actions": actions[:3]
    }
