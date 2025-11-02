import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Page Setup ---
st.set_page_config(page_title="Hydrology Flow App", page_icon="💧", layout="centered")

st.title("💧 Hydrology Flow Calculator")
st.write("Estimate Runoff using the SCS-CN Method and visualize the Hydrograph")

# --- Sidebar Inputs ---
st.sidebar.header("Input Parameters")
rainfall = st.sidebar.number_input("Rainfall (mm)", min_value=0.0, step=1.0)
cn = st.sidebar.number_input("Curve Number (CN)", min_value=30.0, max_value=100.0, step=0.5)
area = st.sidebar.number_input("Catchment Area (km²)", min_value=0.1, step=0.1)
duration = st.sidebar.number_input("Storm Duration (hours)", min_value=1.0, step=0.5)

# --- SCS-CN Runoff Calculation ---
if st.sidebar.button("Calculate Runoff"):
    if cn == 100:
        st.warning("CN cannot be exactly 100. Please use a value below 100.")
    else:
        S = (25400 / cn) - 254  # Potential maximum retention (mm)
        Ia = 0.2 * S            # Initial abstraction (mm)
        if rainfall <= Ia:
            Q = 0
        else:
            Q = ((rainfall - Ia) ** 2) / (rainfall - Ia + S)

        runoff_volume = Q * area * 1000  # m³ (approx)
        
        st.subheader("🌊 Runoff Results")
        st.write(f"**Rainfall (P):** {rainfall:.2f} mm")
        st.write(f"**Runoff (Q):** {Q:.2f} mm")
        st.write(f"**Runoff Volume:** {runoff_volume:,.0f} m³")
        
        # --- Simple Hydrograph Generation ---
        st.subheader("📈 Hydrograph")
        time = np.linspace(0, duration, 50)
        peak = runoff_volume / (duration * 3600)
        discharge = peak * np.exp(-((time - duration / 2) ** 2) / (duration / 4) ** 2)
        
        fig, ax = plt.subplots()
        ax.plot(time, discharge, color='blue', linewidth=2)
        ax.set_xlabel("Time (hours)")
        ax.set_ylabel("Discharge (m³/s)")
        ax.set_title("Synthetic Hydrograph")
        st.pyplot(fig)

        # --- Results Table ---
        data = pd.DataFrame({
            "Time (hr)": np.round(time, 2),
            "Discharge (m³/s)": np.round(discharge, 3)
        })
        st.dataframe(data)

st.markdown("---")
st.caption("Developed using Streamlit | Hydrology Flow App 🌦️")
