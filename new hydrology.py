# hydroflow_app.py
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# ---------------- Page setup ----------------
st.set_page_config(page_title="HydroFlow Estimator", page_icon="💧", layout="wide")
st.title("💧 HydroFlow Estimator — SCS-CN & Strange's Quick Method")
st.write("Enter storm and catchment data, then compute runoff (mm), volume (m³) and simple hydrographs.")

# ---------------- Sidebar inputs ----------------
st.sidebar.header("Storm & Catchment Inputs")

P = st.sidebar.number_input("Rainfall total, P (mm)", min_value=0.0, value=50.0, step=1.0, format="%.2f")
# Offer both area units for convenience
area_unit = st.sidebar.selectbox("Catchment area unit", ["hectares (ha)", "km²"])
if area_unit == "hectares (ha)":
    area_ha = st.sidebar.number_input("Area (ha)", min_value=0.001, value=10.0, step=0.1, format="%.3f")
else:
    area_km2 = st.sidebar.number_input("Area (km²)", min_value=0.0001, value=0.1, step=0.01, format="%.4f")
    area_ha = area_km2 * 100.0  # 1 km² = 100 ha

st.sidebar.markdown("---")
st.sidebar.header("SCS-CN inputs")
# Suggest CN by soil/landuse
cn_suggestions = {
    "Group A (sandy / low runoff) → CN ≈ 30": 30,
    "Group B (loam) → CN ≈ 60": 60,
    "Group C (silty/clay) → CN ≈ 75": 75,
    "Group D (urban/impervious) → CN ≈ 90": 90
}
suggest_label = st.sidebar.selectbox("Suggested soil/land type (gives CN suggestion)", list(cn_suggestions.keys()))
cn_default = cn_suggestions[suggest_label]
CN = st.sidebar.slider("Curve Number (CN) — adjust if known", min_value=30, max_value=99, value=cn_default, step=1)

amc = st.sidebar.selectbox("Antecedent Moisture Condition (AMC) — optional", ["II (normal)", "I (dry)", "III (wet)"])
st.sidebar.caption("If you know AMC, you could adjust CN using standard AMC adjustment tables (not applied automatically here).")

st.sidebar.markdown("---")
st.sidebar.header("Strange's Quick Method (runoff %) inputs")
runoff_pct_map = {
    "Urban built-up (impervious)": 0.60,
    "Agriculture / tilled land": 0.25,
    "Grassland / pasture": 0.15,
    "Forest / dense vegetation": 0.10,
    "Custom (%)": None
}
strange_land = st.sidebar.selectbox("Land use for Strange's method", list(runoff_pct_map.keys()))
if strange_land == "Custom (%)":
    custom_pct = st.sidebar.number_input("Enter runoff percent (0–100)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
    runoff_pct = custom_pct / 100.0
else:
    runoff_pct = runoff_pct_map[strange_land]

st.sidebar.markdown("---")
st.sidebar.header("Hydrograph / output options")
td_hours = st.sidebar.number_input("Runoff duration for hydrograph, td (hours)", min_value=0.1, value=6.0, step=0.5)
npts = st.sidebar.number_input("Hydrograph points (for smoothness)", min_value=10, max_value=500, value=200, step=10)

# ---------------- Calculation functions ----------------
def scs_cn_runoff(P_mm, CN_val):
    """Return Q (mm), S (mm), Ia (mm) using SCS-CN standard formulation."""
    if not (0 < CN_val < 100):
        raise ValueError("CN must be between 0 and 100 (exclusive).")
    S = (25400.0 / CN_val) - 254.0  # mm
    Ia = 0.2 * S
    if P_mm <= Ia:
        Q = 0.0
    else:
        Q = ((P_mm - Ia) ** 2) / (P_mm - Ia + S)
    return Q, S, Ia

def strange_quick_runoff(P_mm, runoff_fraction):
    """Return Q (mm) using Strange's percent method."""
    return P_mm * runoff_fraction

def depth_to_volume(Q_mm, area_ha):
    """Convert depth in mm to volume in m3. area_ha (hectares)."""
    A_m2 = area_ha * 10000.0
    V_m3 = (Q_mm / 1000.0) * A_m2
    return V_m3

def triangular_hydrograph(volume_m3, td_hours, num_points=100):
    """Simple symmetric triangular hydrograph returning times (hr), discharges (m3/s), and peak."""
    if td_hours <= 0:
        raise ValueError("td_hours must be > 0")
    td_s = td_hours * 3600.0
    Qp = 2.0 * volume_m3 / td_s  # m3/s — area of triangle = V
    t = np.linspace(0, td_hours, num_points)
    peak_time = td_hours / 2.0
    Q = np.where(t <= peak_time, (Qp / peak_time) * t, Qp * (1 - (t - peak_time) / peak_time))
    Q[Q < 0] = 0.0
    return t, Q, Qp

# ---------------- Run calculations on button click ----------------
if st.button("Compute Runoff & Generate Hydrographs"):
    # 1) SCS-CN
    try:
        Q_scs_mm, S_val, Ia_val = scs_cn_runoff(P, CN)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    V_scs_m3 = depth_to_volume(Q_scs_mm, area_ha)

    # 2) Strange's quick method
    Q_strange_mm = strange_quick_runoff(P, runoff_pct)
    V_strange_m3 = depth_to_volume(Q_strange_mm, area_ha)

    # 3) Hydrographs
    t_scs, q_scs, Qp_scs = triangular_hydrograph(V_scs_m3, td_hours, num_points=int(npts))
    t_str, q_str, Qp_str = triangular_hydrograph(V_strange_m3, td_hours, num_points=int(npts))

    # ---------------- Display results ----------------
    st.subheader("Results — Runoff Depth & Volume")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**SCS-CN Method**")
        st.write(f"Curve Number (CN): **{CN}**")
        st.write(f"Potential retention S = **{S_val:.2f} mm**")
        st.write(f"Initial abstraction Ia = **{Ia_val:.2f} mm**")
        st.write(f"Runoff depth Q = **{Q_scs_mm:.2f} mm**")
        st.write(f"Runoff volume V = **{V_scs_m3:,.2f} m³**")
        st.write(f"Estimated triangular peak discharge Qp = **{Qp_scs:.3f} m³/s** (triangular hydrograph)")
    with col2:
        st.markdown("**Strange's Quick Method**")
        st.write(f"Selected land use: **{strange_land}**")
        st.write(f"Runoff percentage used = **{runoff_pct*100:.1f}%**")
        st.write(f"Runoff depth Q = **{Q_strange_mm:.2f} mm**")
        st.write(f"Runoff volume V = **{V_strange_m3:,.2f} m³**")
        st.write(f"Estimated triangular peak discharge Qp = **{Qp_str:.3f} m³/s** (triangular hydrograph)")

    # ---------------- Hydrograph plot ----------------
    st.subheader("Hydrograph — Discharge vs Time")
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(t_scs, q_scs, label=f"SCS-CN (Qp={Qp_scs:.3f} m³/s)")
    ax.plot(t_str, q_str, label=f"Strange (Qp={Qp_str:.3f} m³/s)", linestyle="--")
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Discharge (m³/s)")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    # ---------------- Data table & downloads ----------------
    st.subheader("Hydrograph Data (sample)")
    df = pd.DataFrame({
        "time_hr": t_scs,
        "discharge_m3s_scs": q_scs,
        "discharge_m3s_strange": q_str
    })
    st.dataframe(df.head(20))

    # CSV download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download hydrograph CSV", csv, "hydrograph.csv", "text/csv")

    # PNG download of plot
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    st.download_button("Download hydrograph PNG", buf, "hydrograph.png", "image/png")

    st.info("Notes: SCS-CN uses the standard S and Ia formulation. Strange's method uses a fixed runoff percentage to get a quick estimate. Hydrographs here are simple symmetric triangular approximations for demonstration. For research/real design replace triangular_hydrograph() with SCS dimensionless UH or convolution with a unit hydrograph.")
