import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from workflow import (
    run_screening, generate_simulation_data, generate_multi_scenario_data,
    generate_sector_stress_data, calculate_carbon_cost_trajectory,
    build_ai_summary, calculate_ghg, calculate_shadow_carbon_price,
    calculate_climate_cobenefit,
)
from environmental_rules import (
    SECTORS, HAZARDS, RISK_BANDS, PAKISTAN_REGIONS, MOUNTAIN_SYSTEMS,
    REGION_PRIORITIES, MOUNTAIN_PRIORITIES, RESILIENCE_PRIORITIES,
    SCREENING_DISCLAIMER,
)

st.set_page_config(page_title="EcoScreen Pakistan", page_icon="🌍", layout="wide")

st.title("🌍 EcoScreen Pakistan")
st.subheader("Pakistan Climate & Environmental Decision-Support Platform")
st.caption("AI-powered early-stage climate-risk screening for development planning and climate-resilient infrastructure.")

with st.sidebar:
    st.header("📋 Project profile")
    project_name = st.text_input("Project name", "Demo Development Project")
    sector = st.selectbox("Sector", SECTORS)
    province = st.selectbox("Province / territory", PAKISTAN_REGIONS)
    mountain_system = st.selectbox("Mountain / geographic system", ["Not applicable / lowland-coastal setting"] + MOUNTAIN_SYSTEMS)
    project_life = st.slider("Project life (years)", 5, 50, 25)
    capital_cost = st.number_input("Capital cost (USD)", min_value=0.0, value=10_000_000.0, step=500_000.0)
    st.divider()
    st.info("For real projects, replace illustrative inputs with verified climate, hazard, engineering, environmental and emissions data.")

region_priorities = REGION_PRIORITIES.get(province, RESILIENCE_PRIORITIES)
if mountain_system != "Not applicable / lowland-coastal setting":
    priorities = list(dict.fromkeys(region_priorities + MOUNTAIN_PRIORITIES.get(mountain_system, [])))
else:
    priorities = list(region_priorities)

st.info("🎯 **Planning question:** What climate risks could affect this development, and what should we investigate next?")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Screening", "🌧 Climate Indicators", "🩺 CHRI",
    "🌱 GHG & Carbon", "🤝 Co-benefits", "🏗 In-depth Tools", "📄 Report"
])

# ----------------------------------------------------------------------------
# TAB 1 — Screening (fully reactive: every slider/selectbox change recomputes
# the result immediately, so nothing ever needs a second click to "unstick").
# ----------------------------------------------------------------------------
with tab1:
    st.header("Climate & Disaster Risk Screening")
    col1, col2 = st.columns(2)
    with col1:
        exposure = st.slider("Project exposure", 0, 100, 60)
        vulnerability = st.slider("Project vulnerability", 0, 100, 55)
        adaptive_capacity = st.slider("Adaptive capacity", 0, 100, 50)
    with col2:
        hazard = st.selectbox("Primary hazard", HAZARDS)
        sensitivity = st.slider("Sensitivity", 0, 100, 55)
        criticality = st.slider("Asset / service criticality", 0, 100, 60)

    # Recomputed on every rerun -> results always match the widgets on screen.
    result = run_screening(sector, hazard, exposure, vulnerability, adaptive_capacity, sensitivity, criticality)
    result["province"] = province
    result["mountain_system"] = mountain_system
    result["geographic_priorities"] = priorities
    st.session_state["screening"] = result

    r = result
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Risk score", f"{r['risk_score']:.1f}/100")
    c2.metric("Risk band", r["risk_band"])
    c3.metric("Exposure", f"{exposure}/100")
    c4.metric("Adaptive capacity", f"{adaptive_capacity}/100")
    st.progress(min(r["risk_score"] / 100, 1.0))

    g1, g2 = st.columns(2)
    with g1:
        contrib_df = pd.DataFrame({
            "Component": list(r["weighted_contributions"].keys()),
            "Weighted contribution": list(r["weighted_contributions"].values()),
        }).sort_values("Weighted contribution", ascending=True)
        st.plotly_chart(
            px.bar(contrib_df, x="Weighted contribution", y="Component", orientation="h",
                   title="What is driving the risk score?", color="Weighted contribution",
                   color_continuous_scale="OrRd"),
            use_container_width=True,
        )
    with g2:
        radar_fig = go.Figure()
        radar_fig.add_trace(go.Scatterpolar(
            r=r["factors"]["Score"].tolist() + [r["factors"]["Score"].tolist()[0]],
            theta=r["factors"]["Factor"].tolist() + [r["factors"]["Factor"].tolist()[0]],
            fill="toself", name="Current project",
        ))
        radar_fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="Risk factor profile", showlegend=False,
        )
        st.plotly_chart(radar_fig, use_container_width=True)

    st.subheader("🧭 Climate-resilient infrastructure priorities")
    st.caption("Indicative screening priorities; validate them with project-specific hazard, engineering, environmental and socioeconomic data.")
    for item in priorities:
        st.write(f"- {item}")

    st.write("**Priority actions**")
    for item in r["actions"]:
        st.write(f"- {item}")

    if st.button("🔄 Reset sliders to defaults"):
        for key in ["Project exposure", "Project vulnerability", "Adaptive capacity", "Sensitivity", "Asset / service criticality"]:
            st.session_state.pop(key, None)
        st.rerun()

    with st.expander("ℹ️ Screening scope & limitations", expanded=False):
        st.info(SCREENING_DISCLAIMER)

# ----------------------------------------------------------------------------
# TAB 2 — Climate indicators: single-scenario view + all-scenario comparison
# and a combined dual-axis (temperature + precipitation) chart.
# ----------------------------------------------------------------------------
with tab2:
    st.header("Climate Indicators & Illustrative Simulation")
    st.write("These transparent simulations are for demonstration and decision-support prototyping; they are not official forecasts.")
    years = st.slider("Projection horizon", 5, 30, 20)
    baseline_rain = st.number_input("Baseline annual precipitation (mm)", 100.0, 3000.0, 500.0)
    baseline_temp = st.number_input("Baseline mean temperature (°C)", 5.0, 40.0, 24.0)
    scenario = st.selectbox("Illustrative scenario", ["Low change", "Moderate change", "High change"])

    df = generate_simulation_data(years, baseline_rain, baseline_temp, scenario)

    dual = go.Figure()
    dual.add_trace(go.Scatter(x=df["Year"], y=df["Temperature_C"], name="Temperature (°C)", yaxis="y1"))
    dual.add_trace(go.Bar(x=df["Year"], y=df["Precipitation_mm"], name="Precipitation (mm)", yaxis="y2", opacity=0.35))
    dual.update_layout(
        title=f"{scenario}: temperature and precipitation over time",
        yaxis=dict(title="Temperature (°C)"),
        yaxis2=dict(title="Precipitation (mm)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(dual, use_container_width=True)

    st.subheader("Scenario comparison")
    multi = generate_multi_scenario_data(years, baseline_rain, baseline_temp)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            px.line(multi, x="Year", y="Temperature_C", color="Scenario", title="Temperature across scenarios"),
            use_container_width=True,
        )
    with c2:
        st.plotly_chart(
            px.line(multi, x="Year", y="Precipitation_mm", color="Scenario", title="Precipitation across scenarios"),
            use_container_width=True,
        )

    st.dataframe(df, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 3 — CHRI proxy: components chart + trend across a rising-pressure path
# ----------------------------------------------------------------------------
with tab3:
    st.header("Climate & Health Risk Index (CHRI) — project screening proxy")
    st.caption("This is a transparent project-level proxy for demonstration. It does not reproduce the official World Bank CHRI methodology.")
    heat = st.slider("Climate hazard pressure", 0, 100, 60)
    vuln = st.slider("Population vulnerability", 0, 100, 55)
    readiness = st.slider("Health-system readiness", 0, 100, 50)
    chri = 0.40 * heat + 0.35 * vuln + 0.25 * (100 - readiness)
    st.metric("Illustrative project CHRI proxy", f"{chri:.1f}/100")

    c1, c2 = st.columns(2)
    with c1:
        chri_df = pd.DataFrame({
            "Component": ["Climate hazard", "Population vulnerability", "Health-system readiness gap"],
            "Score": [heat, vuln, 100 - readiness],
        })
        st.plotly_chart(px.bar(chri_df, x="Component", y="Score", title="CHRI proxy components", color="Component"), use_container_width=True)
    with c2:
        horizon = np.arange(1, 21)
        trend = np.clip(chri + np.linspace(-10, 10, len(horizon)) + np.random.default_rng(42).normal(0, 1.5, len(horizon)), 0, 100)
        trend_df = pd.DataFrame({"Year": horizon, "CHRI proxy": np.round(trend, 1)})
        st.plotly_chart(px.line(trend_df, x="Year", y="CHRI proxy", title="Illustrative 20-year CHRI proxy trend", markers=True), use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 4 — GHG & carbon: breakdown donut + a live carbon-cost trajectory
# ----------------------------------------------------------------------------
with tab4:
    st.header("GHG Accounting & Shadow Carbon")
    electricity_mwh = st.number_input("Electricity use (MWh/year)", 0.0, value=5000.0)
    fuel_l = st.number_input("Liquid fuel (litres/year)", 0.0, value=100000.0)
    travel_km = st.number_input("Vehicle travel (km/year)", 0.0, value=500000.0)
    ef_elec = st.number_input("Electricity EF (tCO₂e/MWh)", 0.0, value=0.45)
    ef_fuel = st.number_input("Fuel EF (kgCO₂e/litre)", 0.0, value=2.68)
    ef_travel = st.number_input("Travel EF (kgCO₂e/km)", 0.0, value=0.18)
    ghg = calculate_ghg(electricity_mwh, fuel_l, travel_km, ef_elec, ef_fuel, ef_travel)
    st.metric("Estimated annual GHG emissions", f"{ghg['total_tco2e']:,.1f} tCO₂e/year")

    breakdown_df = pd.DataFrame(ghg["breakdown"])
    c1, c2 = st.columns([1, 1])
    with c1:
        st.dataframe(breakdown_df, use_container_width=True)
        st.plotly_chart(px.pie(breakdown_df, names="Source", values="tCO2e", hole=0.45, title="Emissions by source"), use_container_width=True)
    with c2:
        carbon_price = st.number_input("Illustrative shadow carbon price (USD/tCO₂e)", 0.0, value=50.0)
        price_escalation = st.slider("Illustrative annual carbon-price escalation (%)", 0.0, 15.0, 3.0)
        carbon = calculate_shadow_carbon_price(ghg["total_tco2e"], project_life, carbon_price)
        st.metric("Undiscounted lifetime carbon cost", f"${carbon:,.0f}")

        cost_df = calculate_carbon_cost_trajectory(ghg["total_tco2e"], project_life, carbon_price, price_escalation)
        cost_fig = go.Figure()
        cost_fig.add_trace(go.Bar(x=cost_df["Year"], y=cost_df["Annual carbon cost (USD)"], name="Annual cost", yaxis="y1"))
        cost_fig.add_trace(go.Scatter(x=cost_df["Year"], y=cost_df["Cumulative carbon cost (USD)"], name="Cumulative cost", yaxis="y2"))
        cost_fig.update_layout(
            title="Shadow carbon cost over project life",
            yaxis=dict(title="Annual cost (USD)"),
            yaxis2=dict(title="Cumulative cost (USD)", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(cost_fig, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 5 — Co-benefits: bar chart + radar
# ----------------------------------------------------------------------------
with tab5:
    st.header("Climate Co-benefits")
    mitigation = st.slider("Mitigation contribution", 0, 100, 50)
    adaptation = st.slider("Adaptation contribution", 0, 100, 60)
    social = st.slider("Social / development co-benefits", 0, 100, 55)
    score = calculate_climate_cobenefit(mitigation, adaptation, social)
    st.metric("Illustrative co-benefit score", f"{score:.1f}/100")

    c1, c2 = st.columns(2)
    with c1:
        cb = pd.DataFrame({"Dimension": ["Mitigation", "Adaptation", "Social / development"], "Score": [mitigation, adaptation, social]})
        st.plotly_chart(px.bar(cb, x="Dimension", y="Score", title="Climate co-benefit profile", color="Dimension"), use_container_width=True)
    with c2:
        dims = ["Mitigation", "Adaptation", "Social / development"]
        vals = [mitigation, adaptation, social]
        radar = go.Figure()
        radar.add_trace(go.Scatterpolar(r=vals + [vals[0]], theta=dims + [dims[0]], fill="toself", name="Co-benefits"))
        radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), title="Co-benefit balance", showlegend=False)
        st.plotly_chart(radar, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 6 — Sector in-depth tools: single sector + multi-sector comparison
# ----------------------------------------------------------------------------
with tab6:
    st.header("Sector In-depth Screening Assessments")
    all_sectors = ["Agriculture", "Energy", "Health", "Transportation", "Water"]
    selected = st.selectbox("Select assessment", all_sectors)
    compare_sectors = st.multiselect("Compare against other sectors", [s for s in all_sectors if s != selected])
    intensity = st.slider("Climate stress intensity", 0, 100, 60)
    resilience = st.slider("Existing resilience", 0, 100, 45)
    st.caption("Both sliders are unitless illustrative index scores (0 = none, 100 = maximum), not measured physical quantities "
               "(e.g. not °C, mm, or a probability). For real projects, replace them with a validated hazard/exposure index "
               "and a documented resilience/readiness index.")

    sector_set = [selected] + compare_sectors
    sim = generate_sector_stress_data(20, intensity, resilience, sector_set)
    st.plotly_chart(
        px.line(sim, x="Year", y="Risk_Index", color="Sector",
                title=f"Simulated climate stress trajectory: {', '.join(sector_set)}"),
        use_container_width=True,
    )

    focus = {
        "Agriculture": ["Heat stress", "Rainfall variability", "Drought", "Flooding", "Water availability", "Crop/livestock resilience"],
        "Energy": ["Heat impacts", "Hydropower/water availability", "Flooding", "Grid resilience", "Cooling demand"],
        "Health": ["Heat-health", "Vector-borne disease", "Water-borne disease", "Air quality", "Health-system readiness"],
        "Transportation": ["Flooding", "Extreme heat", "Landslides", "Road/bridge resilience", "Supply-chain disruption"],
        "Water": ["Drought", "Flooding", "Water quality", "Demand pressure", "Catchment resilience"],
    }[selected]
    st.write(f"**Assessment focus — {selected}**")
    for x in focus:
        st.write(f"- {x}")

# ----------------------------------------------------------------------------
# TAB 7 — AI report + export
# ----------------------------------------------------------------------------
with tab7:
    st.header("🤖 AI Decision-Support Summary")
    if st.button("Generate Groq AI screening summary", type="primary"):
        context = st.session_state.get("screening", {})
        with st.spinner("Generating climate-risk explanation with Groq..."):
            try:
                summary_text = build_ai_summary(project_name, sector, province, mountain_system, context, priorities)
                st.session_state["ai_summary"] = summary_text
            except Exception as exc:
                st.session_state["ai_summary"] = None
                st.error(f"Groq request failed: {exc}")
                st.info("Check that GROQ_API_KEY is present in Streamlit Secrets and that the selected Groq model is available.")

    if st.session_state.get("ai_summary"):
        st.markdown(st.session_state["ai_summary"])

    st.divider()
    screening = st.session_state.get("screening", {})
    export = pd.DataFrame([{
        "project_name": project_name, "sector": sector, "province": province,
        "mountain_system": mountain_system, "project_life_years": project_life,
        "capital_cost_usd": capital_cost,
        "hazard": screening.get("hazard", ""), "risk_score": screening.get("risk_score", ""),
        "risk_band": screening.get("risk_band", ""), "resilience_priorities": "; ".join(priorities),
    }])
    st.download_button("Download screening inputs as CSV", export.to_csv(index=False), "project_screening_inputs.csv", "text/csv")

st.divider()
st.success("🌱 **Climate-resilient infrastructure focus:** move from “build first, deal with climate risks later” toward “consider climate risks during planning.”")
st.caption("EcoScreen Pakistan is a prototype decision-support application. Validate findings with qualified climate, environmental, engineering, health and regulatory specialists before real investment or compliance decisions.")

with st.expander("🛣️ Future production upgrades", expanded=False):
    st.markdown(
        "Replace illustrative simulations with validated CCKP, PMD, ERA5, CHIRPS, CMIP6 and/or verified national "
        "datasets as legally and technically appropriate. Add data provenance, dates, uncertainty, geospatial "
        "layers, validated sector indicators, and documented emission/carbon methodologies."
    )
