import os
import numpy as np
import pandas as pd

RISK_ACTIONS = {
    "Low": ["Continue routine climate screening.", "Document assumptions and monitor key indicators."],
    "Moderate": ["Add climate-resilient design measures.", "Conduct targeted site and hazard assessment."],
    "High": ["Undertake a detailed climate risk and adaptation assessment.", "Quantify critical failure modes and adaptation costs.", "Engage relevant technical specialists."],
    "Critical": ["Do not rely on screening alone.", "Commission a project-specific climate/disaster risk assessment.", "Review project design, siting, alternatives and residual risk before proceeding."],
}

HAZARD_PRESSURE = {
    "Flood": 1.00, "Extreme heat": 0.95, "Drought": 0.90,
    "Extreme precipitation": 0.95, "Landslide": 0.85,
    "Storm": 0.80, "Wildfire": 0.70, "Sea-level rise": 0.90,
}

SCENARIO_MULTIPLIERS = {"Low change": 0.35, "Moderate change": 0.70, "High change": 1.10}


def run_screening(sector, hazard, exposure, vulnerability, adaptive_capacity, sensitivity, criticality):
    """Compute an illustrative composite risk score and supporting factor breakdown."""
    hazard_pressure = HAZARD_PRESSURE.get(hazard, 0.80)
    weighted = {
        "Exposure": 0.22 * exposure,
        "Vulnerability": 0.20 * vulnerability,
        "Sensitivity": 0.18 * sensitivity,
        "Criticality": 0.16 * criticality,
        "Adaptive capacity gap": 0.16 * (100 - adaptive_capacity),
        "Hazard pressure": 0.08 * (hazard_pressure * 100),
    }
    score = float(np.clip(sum(weighted.values()), 0, 100))

    if score < 25:
        band = "Low"
    elif score < 50:
        band = "Moderate"
    elif score < 75:
        band = "High"
    else:
        band = "Critical"

    factors = pd.DataFrame({
        "Factor": ["Exposure", "Vulnerability", "Sensitivity", "Criticality", "Adaptive capacity"],
        "Score": [exposure, vulnerability, sensitivity, criticality, adaptive_capacity],
    })

    return {
        "risk_score": score,
        "risk_band": band,
        "sector": sector,
        "hazard": hazard,
        "actions": RISK_ACTIONS[band],
        "weighted_contributions": weighted,
        "factors": factors,
    }


def generate_simulation_data(years, baseline_rain, baseline_temp, scenario, seed=None):
    """Illustrative temperature/precipitation trajectory for a single scenario."""
    m = SCENARIO_MULTIPLIERS[scenario]
    t = np.arange(1, int(years) + 1)
    rng = np.random.default_rng(seed if seed is not None else abs(hash((years, baseline_rain, baseline_temp, scenario))) % (2**32))
    noise_t = rng.normal(0, 0.08, size=len(t))
    noise_p = rng.normal(0, 0.02, size=len(t))
    temperature = baseline_temp + (0.025 * m) * t + 0.15 * np.sin(t / 2) + noise_t
    precipitation = baseline_rain * (1 + 0.003 * m * t + 0.08 * np.sin(t / 2.8)) * (1 + noise_p)
    return pd.DataFrame({
        "Year": t,
        "Temperature_C": np.round(temperature, 2),
        "Precipitation_mm": np.round(precipitation, 1),
    })


def generate_multi_scenario_data(years, baseline_rain, baseline_temp):
    """Same simulation run across all three illustrative scenarios, stacked for comparison charts."""
    frames = []
    for scenario in SCENARIO_MULTIPLIERS:
        df = generate_simulation_data(years, baseline_rain, baseline_temp, scenario, seed=hash(scenario) % (2**32))
        df["Scenario"] = scenario
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def calculate_ghg(electricity_mwh, fuel_l, travel_km, ef_elec, ef_fuel, ef_travel):
    electricity = electricity_mwh * ef_elec
    fuel = fuel_l * ef_fuel / 1000
    travel = travel_km * ef_travel / 1000
    return {"total_tco2e": electricity + fuel + travel, "breakdown": [
        {"Source": "Electricity", "tCO2e": electricity},
        {"Source": "Liquid fuel", "tCO2e": fuel},
        {"Source": "Vehicle travel", "tCO2e": travel},
    ]}


def calculate_shadow_carbon_price(annual_tco2e, years, price_usd_per_tco2e):
    return float(annual_tco2e * years * price_usd_per_tco2e)


def calculate_carbon_cost_trajectory(annual_tco2e, years, price_usd_per_tco2e, price_escalation_pct=0.0):
    """Year-by-year (optionally escalating) shadow carbon cost, for a trend chart."""
    t = np.arange(1, int(years) + 1)
    price_path = price_usd_per_tco2e * (1 + price_escalation_pct / 100) ** (t - 1)
    annual_cost = annual_tco2e * price_path
    cumulative_cost = np.cumsum(annual_cost)
    return pd.DataFrame({
        "Year": t,
        "Carbon price (USD/tCO2e)": np.round(price_path, 2),
        "Annual carbon cost (USD)": np.round(annual_cost, 0),
        "Cumulative carbon cost (USD)": np.round(cumulative_cost, 0),
    })


def calculate_climate_cobenefit(mitigation, adaptation, social):
    return float(0.40 * mitigation + 0.40 * adaptation + 0.20 * social)


def generate_sector_stress_data(years, intensity, resilience, sectors):
    """Illustrative climate-stress trajectory for one or more sectors, for comparison charts."""
    t = np.arange(1, int(years) + 1)
    frames = []
    sector_offset = {"Agriculture": 4, "Energy": 0, "Health": -3, "Transportation": 2, "Water": 6}
    for s in sectors:
        offset = sector_offset.get(s, 0)
        risk = np.clip(intensity + offset + np.linspace(0, 20, len(t)) - resilience * 0.4, 0, 100)
        frames.append(pd.DataFrame({"Year": t, "Risk_Index": np.round(risk, 1), "Sector": s}))
    return pd.concat(frames, ignore_index=True)


def build_deterministic_summary(project_name, sector, province, mountain_system, screening, priorities):
    if not screening:
        return "Run the climate risk screening first."
    priorities_text = "\n".join(f"- {p}" for p in priorities)
    actions_text = "\n".join("- " + a for a in screening["actions"])
    return f"""### Screening Summary

**Project:** {project_name}

**Sector:** {sector}

**Location:** {province}

**Geographic system:** {mountain_system}

**Screening risk:** **{screening['risk_band']} ({screening['risk_score']:.1f}/100)**

**Primary hazard:** {screening['hazard']}

#### Climate-resilient infrastructure priorities
{priorities_text}

#### Recommended next steps
{actions_text}

> This automated screening is based on user-provided inputs. Validate material findings with verified site-specific climate, hazard, engineering, environmental and socioeconomic data.
"""


def build_ai_summary(project_name, sector, province, mountain_system, screening, priorities):
    """Generate an AI explanation with Groq. Falls back to a deterministic summary if no key is configured."""
    if not screening:
        return "Run the climate risk screening first."

    api_key = os.getenv("GROQ_API_KEY")
    try:
        import streamlit as st
        api_key = api_key or st.secrets.get("GROQ_API_KEY")
    except Exception:
        pass

    if not api_key:
        return build_deterministic_summary(project_name, sector, province, mountain_system, screening, priorities) + "\n\n**Groq AI note:** Add `GROQ_API_KEY` to Streamlit Secrets to enable the LLM-generated explanation."

    from groq import Groq
    client = Groq(api_key=api_key)
    prompt = f"""
You are an environmental and climate-risk decision-support assistant for Pakistan.
Distinguish screening-level findings from verified technical findings. Do not invent site measurements,
forecasts, regulations, legal thresholds, citations, or site-specific hazards. Use cautious language.

Project: {project_name}
Sector: {sector}
Province/territory: {province}
Geographic system: {mountain_system}
Risk band: {screening['risk_band']}
Risk score: {screening['risk_score']:.1f}/100
Primary hazard: {screening['hazard']}
Priority actions: {screening['actions']}
Geographic resilience priorities: {priorities}

Answer with these headings:
1. Screening interpretation
2. Main climate-risk considerations
3. Climate-resilient infrastructure priorities
4. What to investigate next
5. Key data gaps and assumptions

Keep it practical for early-stage development planning. Emphasize the shift from "build first, deal with climate risks later"
toward "consider climate risks during planning". State clearly that this is not an EIA, engineering design, regulatory approval,
or site-specific forecast.
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You provide careful, evidence-oriented climate-risk decision support."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1800,
    )
    return response.choices[0].message.content
