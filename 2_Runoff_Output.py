import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("📊 Runoff Calculation Results")

if "method" not in st.session_state:
    st.error("⚠️ Please go to the Method Selection page first.")
    st.stop()

method = st.session_state["method"]
st.write(f"### Method Used: {method}")

if method == "SCS-CN":
    P = st.session_state["P"]
    CN = st.session_state["CN"]
    S = (25400 / CN) - 254
    Q = ((P - 0.2 * S) ** 2) / (P + 0.8 * S) if P > 0.2 * S else 0

elif method == "Stranger’s":
    P = st.session_state["P"]
    C = st.session_state["C"]
    Q = C * P

st.success(f"💧 Estimated Runoff (Q): **{Q:.2f} mm**")

time = np.arange(0, 10, 1)
runoff = np.maximum(0, Q * np.exp(-0.3 * time))

fig, ax = plt.subplots()
ax.plot(time, runoff, marker='o', color='blue', linewidth=2)
ax.set_xlabel("Time (hr)")
ax.set_ylabel("Runoff (mm)")
ax.set_title("Hydrograph")
st.pyplot(fig)

df = pd.DataFrame({"Time (hr)": time, "Runoff (mm)": runoff})
st.dataframe(df)

st.download_button(
    "📥 Download Runoff Data as CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="runoff_results.csv",
    mime="text/csv"
)

st.info("Use the sidebar to go back to Methods or Home.")
