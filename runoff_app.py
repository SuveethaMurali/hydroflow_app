import streamlit as st

st.set_page_config(page_title="Runoff Estimation App", page_icon="💧", layout="centered")

st.title("💧 Runoff Estimation App")
st.write("Estimate surface runoff using SCS-CN or Rational Method.")

# Method selection
method = st.selectbox("Select Method:", ["SCS-CN Method", "Rational Method"])

if method == "SCS-CN Method":
    st.subheader("SCS-CN Method Inputs")
    P = st.number_input("Rainfall (mm):", min_value=0.0, step=0.1)
    CN = st.number_input("Curve Number (CN):", min_value=30.0, max_value=100.0, step=1.0)

    if st.button("Calculate Runoff"):
        if P > 0 and CN > 0:
            S = (25400 / CN) - 254
            if P > 0.2 * S:
                Q = ((P - 0.2 * S) ** 2) / (P + 0.8 * S)
            else:
                Q = 0
            st.success(f"Estimated Runoff (Q) = {Q:.2f} mm")
        else:
            st.warning("Please enter valid values for Rainfall and CN.")

elif method == "Rational Method":
    st.subheader("Rational Method Inputs")
    C = st.number_input("Runoff Coefficient (C):", min_value=0.1, max_value=1.0, step=0.1)
    I = st.number_input("Rainfall Intensity (mm/hr):", min_value=0.0, step=0.1)
    A = st.number_input("Catchment Area (hectares):", min_value=0.0, step=0.1)

    if st.button("Calculate Runoff"):
        if C > 0 and I > 0 and A > 0:
            Q = C * I * A
            st.success(f"Estimated Runoff (Q) = {Q:.2f} (mm·ha/hr units)")
        else:
            st.warning("Please enter valid values for all inputs.")

st.markdown("---")
st.caption("Developed for educational use.")
