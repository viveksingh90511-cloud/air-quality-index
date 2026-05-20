import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_disease_outbreak():
    st.title("🦠 Disease Outbreak Prediction")
    st.markdown("Predict the probability of respiratory and cardiovascular outbreaks based on prolonged AQI exposure.")

    # Sidebar inputs
    st.sidebar.header("Outbreak Simulation Parameters")
    city = st.sidebar.selectbox("City", ["Delhi", "Mumbai", "Kolkata", "Bangalore", "Lucknow"])
    current_aqi = st.sidebar.slider("Simulated AQI Level", 50, 500, 250)
    exposure_days = st.sidebar.slider("Exposure Duration (Days)", 1, 30, 7)
    
    # Calculate simulated risks
    base_factor = min(current_aqi / 300.0, 1.0)
    exposure_multiplier = min(1.0 + (exposure_days / 15.0), 2.5)
    
    asthma_risk = min(base_factor * 0.65 * exposure_multiplier * 100, 99.9)
    resp_infection_risk = min(base_factor * 0.45 * exposure_multiplier * 100, 99.9)
    cardio_risk = min(base_factor * 0.30 * exposure_multiplier * 100, 99.9)
    allergy_risk = min(base_factor * 0.50 * exposure_multiplier * 100, 99.9)

    st.subheader(f"Outbreak Risk Profile for {city}")
    st.markdown(f"**Current AQI**: {current_aqi}  |  **Exposure Window**: {exposure_days} days")

    col1, col2, col3, col4 = st.columns(4)
    
    def get_color(risk):
        if risk < 30: return "green"
        elif risk < 60: return "orange"
        else: return "red"

    with col1:
        st.metric("Asthma Exacerbation", f"{asthma_risk:.1f}%", delta=f"{asthma_risk - 15:.1f}% vs Avg", delta_color="inverse")
    with col2:
        st.metric("Respiratory Infections", f"{resp_infection_risk:.1f}%", delta=f"{resp_infection_risk - 10:.1f}% vs Avg", delta_color="inverse")
    with col3:
        st.metric("Cardiovascular Events", f"{cardio_risk:.1f}%", delta=f"{cardio_risk - 5:.1f}% vs Avg", delta_color="inverse")
    with col4:
        st.metric("Allergic Rhinitis", f"{allergy_risk:.1f}%", delta=f"{allergy_risk - 20:.1f}% vs Avg", delta_color="inverse")

    st.divider()

    st.subheader("🏥 Projected Hospital Admissions (Next 14 Days)")
    
    # Generate time series for hospital projections
    dates = [datetime.now() + timedelta(days=i) for i in range(14)]
    
    # Create baseline and projected admission lines
    baseline = [50 + 5*np.sin(i) for i in range(14)]
    projected = [b + (current_aqi * exposure_days * 0.05) * (1.1 ** i) for i, b in enumerate(baseline)]
    
    df_proj = pd.DataFrame({
        "Date": dates,
        "Baseline Admissions": baseline,
        "Projected Admissions (AQI Adjusted)": projected
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_proj["Date"], y=df_proj["Baseline Admissions"], 
                             mode='lines+markers', name='Baseline Expected', line=dict(color='green', dash='dash')))
    fig.add_trace(go.Scatter(x=df_proj["Date"], y=df_proj["Projected Admissions (AQI Adjusted)"], 
                             mode='lines+markers', name='Projected (AQI Impact)', line=dict(color='red')))
    
    fig.update_layout(
        title=f"Projected Daily Respiratory Hospital Admissions in {city}",
        xaxis_title="Date",
        yaxis_title="Daily Admissions",
        hovermode="x unified",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("💡 Public Health Recommendations")
    if current_aqi > 200:
        st.error("🚨 **CRITICAL HEALTH EMERGENCY**")
        st.markdown("- Issue city-wide N95 mask mandate.\n- Advise vulnerable populations to evacuate or remain in filtered indoor environments.\n- Hospitals must prepare for a 40-60% surge in respiratory admissions.")
    elif current_aqi > 100:
        st.warning("⚠️ **ELEVATED HEALTH RISK**")
        st.markdown("- Distribute masks to sensitive groups.\n- Limit strenuous outdoor activities.\n- Stockpile asthma medication at local pharmacies.")
    else:
        st.success("✅ **SAFE CONDITIONS**")
        st.markdown("- Air quality poses minimal outbreak risk.\n- Continue standard monitoring.")

if __name__ == "__main__":
    render_disease_outbreak()
