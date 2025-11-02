import streamlit as st

st.set_page_config(
    page_title="HydroFlow - Runoff Estimation System",
    page_icon="💧",
    layout="centered"
)

st.title("💧 HydroFlow - Runoff Estimation Dashboard")
st.markdown("""
### Welcome to **HydroFlow**
An interactive web application designed to estimate **surface runoff** 
using hydrological methods like:
- 🌿 **SCS Curve Number (CN) Method**
- 🌊 **Stranger’s Method**

---

#### 🧭 How it works
1. Go to the **Methods Page** to choose a calculation method.  
2. Enter rainfall and other required parameters.  
3. View the **Hydrograph**, result table, and estimated runoff.

---

#### 🏫 Project Details
- **Developed by:** Your Name  
- **Institution:** Your College Name  
- **Department:** Civil Engineering
""")

st.info("➡️ Navigate using the sidebar to select your method and start your calculation.")
