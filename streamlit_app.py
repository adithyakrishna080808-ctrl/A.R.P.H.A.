import streamlit as st
import pandas as pd

st.set_page_config(page_title="A.R.P.H.A – Himachal Pilot", layout="wide")

st.title("A.R.P.H.A – Himachal Pilot")
st.markdown("**Advanced Radar for Precipitation and Hazard Alerts**")

# -------------------------
# Load rainfall data
# -------------------------
df = pd.read_csv("rainfall.csv")

# -------------------------
# Risk computation
# -------------------------
def compute_risk(row):
    # Simple rule-based risk
    if row["rainfall_mm_1h"] > 50 or row["rainfall_mm_3d"] > 130:
        return "High"
    elif row["rainfall_mm_1h"] > 30 or row["rainfall_mm_3d"] > 100:
        return "Medium"
    else:
        return "Low"

df["risk"] = df.apply(compute_risk, axis=1)

# -------------------------
# Dashboard – Risk Table
# -------------------------
st.header("1. Town-wise Flash Flood Risk")

st.write("Current rainfall and computed risk for selected towns in Himachal Pradesh.")

st.dataframe(
    df[["village", "rainfall_mm_1h", "rainfall_mm_3d", "risk"]]
)

# -------------------------
# Map
# -------------------------
st.header("2. Risk Map")

st.write("Map shows location of towns. Color/size does not encode risk in this simple demo.")

st.map(df[["lat", "lon"]])

# -------------------------
# Alerts
# -------------------------
st.header("3. Alerts")

high_risk = df[df["risk"] == "High"]

if len(high_risk) > 0:
    st.error("High flash flood risk detected in the following towns:")
    for _, row in high_risk.iterrows():
        st.write(
            f"🚨 **{row['village']}**: High risk in the next 3 hours due to heavy rainfall."
        )
else:
    st.success("No high-risk towns at the moment based on current rainfall.")

# -------------------------
# Simulate heavy rain
# -------------------------
st.header("4. Scenario Simulation")

st.write("Click the button below to simulate an extreme rainfall event and see how risk changes.")

if st.button("Simulate Heavy Rain"):
    # Simulate heavy rain in a couple of towns
    df.loc[df["village"] == "Manali", "rainfall_mm_1h"] = 65
    df.loc[df["village"] == "Manali", "rainfall_mm_3d"] = 150
    df.loc[df["village"] == "Bhuntar", "rainfall_mm_1h"] = 70
    df.loc[df["village"] == "Bhuntar", "rainfall_mm_3d"] = 160

    df["risk"] = df.apply(compute_risk, axis=1)

    st.write("Updated rainfall and risk after simulation:")

    st.dataframe(
        df[["village", "rainfall_mm_1h", "rainfall_mm_3d", "risk"]]
    )

    high_risk_sim = df[df["risk"] == "High"]
    st.write("Updated alerts:")
    if len(high_risk_sim) > 0:
        st.error("High flash flood risk detected after simulation:")
        for _, row in high_risk_sim.iterrows():
            st.write(
                f"🚨 **{row['village']}**: High risk in the next 3 hours due to simulated heavy rainfall."
            )
    else:
        st.success("Still no high-risk towns after simulation.")

# -------------------------
# About A.R.P.H.A
# -------------------------
st.header("About A.R.P.H.A")

st.markdown(
    """
**A.R.P.H.A (Advanced Radar for Precipitation and Hazard Alerts)** is an early warning system for flash floods in hilly regions.

- **Current pilot**: Kullu–Manali–Mandi corridor, Himachal Pradesh.  
- **Core capability**: Uses rainfall data (1-hour and 3-day) to estimate town-level flash flood risk (Low/Medium/High) and generate alerts.  
- **Multi-source design**: In a full deployment, it will integrate IMD rainfall, satellite data (GPM/IMERG), terrain (DEM), and soil moisture.  
- **Future extension**: For upper Himachal (Lahaul & Spiti, Kinnaur), A.R.P.H.A can be extended to classify rivers at risk from glacial spill / GLOF events by integrating glacial lake and terrain data.

This prototype demonstrates the core idea with a simple rule-based model and a small set of towns.
"""
)