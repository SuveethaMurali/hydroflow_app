import streamlit as st

st.title("🧩 Method Selection and Input")

method = st.selectbox(
    "Choose the Method:",
    ["Select...", "SCS-CN Method", "Stranger’s Method"]
)

st.write("---")

if method == "SCS-CN Method":
    st.subheader("SCS Curve Number Method")
    st.latex(r"Q = \frac{(P - 0.2S)^2}{(P + 0.8S)}, \quad S = \frac{25400}{CN} - 254")

    P = st.number_input("Enter Rainfall (P) in mm", min_value=0.0, step=0.1)
    CN = st.number_input("Enter Curve Number (CN)", min_value=30.0, max_value=100.0, step=0.1)

    if st.button("Calculate Runoff"):
        st.session_state["method"] = "SCS-CN"
        st.session_state["P"] = P
        st.session_state["CN"] = CN
        st.switch_page("pages/2_Runoff_Output.py")

elif method == "Stranger’s Method":
    st.subheader("Stranger’s Method")
    st.latex(r"Q = C \times P")

    P = st.number_input("Enter Rainfall (P) in mm", min_value=0.0, step=0.1)
    C = st.number_input("Enter Runoff Coefficient (C)", min_value=0.0, max_value=1.0, step=0.01)

    if st.button("Calculate Runoff"):
        st.session_state["method"] = "Stranger’s"
        st.session_state["P"] = P
        st.session_state["C"] = C
        st.switch_page("pages/2_Runoff_Output.py")

else:
    st.warning("Please select a method to continue.")
