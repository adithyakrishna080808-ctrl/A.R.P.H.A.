import streamlit as st
import pandas as pd

st.set_page_config(page_title="A.R.P.H.A – Himachal Pilot", layout="wide")

st.title("A.R.P.H.A – Himachal Pilot")
st.markdown("**Advanced Radar for Precipitation and Hazard Alerts**")

# -------------------------
# Load data
# -------------------------
df = pd.read_csv("data.csv")

# -------------------------
# Helper: slope score
# -------------------------
def slope_score(slope_class):
    if slope_class == "High":
        return 30
    elif slope_class == "Medium":
        return 20
    else:
        return 10

# -------------------------
# Multi-source risk computation
# -------------------------
def compute_risk_score(row):
    # Rainfall component (0–40)
    rain_score = 0
    if row["rainfall_mm_1h"] > 50 or row["rainfall_mm_3d"] > 130:
        rain_score = 40
    elif row["rainfall_mm_1h"] > 30 or row["rainfall_mm_3d"] > 100:
        rain_score = 25
    else:
        rain_score = 10

    # Slope component (0–30)
    s_score = slope_score(row["slope_class"])

    # Soil moisture component (0–20)
    # Higher soil moisture → higher risk
    if row["soil_moisture_pct"] > 60:
        soil_score = 20
    elif row["soil_moisture_pct"] > 45:
        soil_score = 12
    else:
        soil_score = 5

    # Historical events component (0–10)
    hist_score = 10 if row["historical_events"] == 1 else 0

    total_score = rain_score + s_score + soil_score + hist_score
    return total_score  # 0–100

def risk_category(score):
    if score >= 70:
        return "High"
    elif score >= 45:
        return "Medium"
    else:
        return "Low"

df["risk_score"] = df.apply(compute_risk_score, axis=1)
df["risk_category"] = df["risk_score"].apply(risk_category)

# -------------------------
# Sidebar – Info
# -------------------------
st.sidebar.header("About A.R.P.H.A")
st.sidebar.markdown(
    """
**A.R.P.H.A** is an early warning system for flash floods in hilly regions.

**Data layers used:**
- Rainfall (1-hour, 3-day)  
- Terrain (slope class)  
- Soil moisture  
- Historical flash flood/landslide events  

**Risk score:** 0–100  
**Risk categories:** Low (<45), Medium (45–69), High (≥70)
"""
)

# -------------------------
# Dashboard – Overview
# -------------------------
st.header("1. Town-wise Multi-Source Risk Assessment")

st.write(
    "This table shows all input features and the computed risk score & category for each town."
)

st.dataframe(
    df[
        [
            "town",
            "rainfall_mm_1h",
            "rainfall_mm_3d",
            "slope_class",
            "soil_moisture_pct",
            "historical_events",
            "risk_score",
            "risk_category",
        ]
    ]
)

# -------------------------
# Map
# -------------------------
st.header("2. Risk Map")

st.write(
    "Map shows town locations. In a full deployment, risk levels can be shown with colored markers."
)

st.map(df[["lat", "lon"]])

# -------------------------
# Alerts
# -------------------------
st.header("3. Alerts")

high_risk = df[df["risk_category"] == "High"]

if len(high_risk) > 0:
    st.error("High flash flood risk detected in the following towns:")
    for _, row in high_risk.iterrows():
        st.write(
            f"🚨 **{row['town']}**: Risk score **{row['risk_score']}** – High risk in the next 3 hours."
        )
        st.write(
            f"- Rainfall: {row['rainfall_mm_1h']} mm (1h), {row['rainfall_mm_3d']} mm (3d)  "
            f"| Slope: {row['slope_class']} | Soil moisture: {row['soil_moisture_pct']}%  "
            f"| Past events: {'Yes' if row['historical_events'] else 'No'}"
        )
else:
    st.success("No high-risk towns at the moment based on current multi-source data.")

# -------------------------
# Scenario Simulation
# -------------------------
st.header("4. Scenario Simulation")

st.write(
    "Simulate an extreme rainfall event with high soil saturation to see how risk changes."
)

if st.button("Simulate Extreme Event"):
    # Simulate heavy rain + high soil moisture in some towns
    df.loc[df["town"] == "Manali", "rainfall_mm_1h"] = 65
    df.loc[df["town"] == "Manali", "rainfall_mm_3d"] = 150
    df.loc[df["town"] == "Manali", "soil_moisture_pct"] = 75

    df.loc[df["town"] == "Bhuntar", "rainfall_mm_1h"] = 70
    df.loc[df["town"] == "Bhuntar", "rainfall_mm_3d"] = 160
    df.loc[df["town"] == "Bhuntar", "soil_moisture_pct"] = 80

    df["risk_score"] = df.apply(compute_risk_score, axis=1)
    df["risk_category"] = df["risk_score"].apply(risk_category)

    st.write("Updated data after simulation:")

    st.dataframe(
        df[
            [
                "town",
                "rainfall_mm_1h",
                "rainfall_mm_3d",
                "slope_class",
                "soil_moisture_pct",
                "historical_events",
                "risk_score",
                "risk_category",
            ]
        ]
    )

    high_risk_sim = df[df["risk_category"] == "High"]
    st.write("Updated alerts after simulation:")

    if len(high_risk_sim) > 0:
        st.error("High flash flood risk detected after simulation:")
        for _, row in high_risk_sim.iterrows():
            st.write(
                f"🚨 **{row['town']}**: Risk score **{row['risk_score']}** – High risk in the next 3 hours."
            )
    else:
        st.success("Still no high-risk towns after simulation.")

# -------------------------
# Data Layers Explanation
# -------------------------
st.header("5. Data Layers Used")

st.markdown(
    """
A.R.P.H.A uses a **multi-source risk model**:

- **Rainfall**  
  - 1-hour intensity and 3-day antecedent rainfall from IMD / satellite.  
  - High short-term rain or prolonged rain increases risk.

- **Terrain (Slope)**  
  - Steeper slopes (High slope class) increase runoff speed and landslide potential.  
  - Represented here as slope class: Low / Medium / High.

- **Soil Moisture**  
  - Indicates how saturated the ground is (from SMAP / ESA CCI soil moisture data).  
  - Saturated soil → less infiltration → higher flash flood risk.

- **Historical Events**  
  - Towns with past flash floods/landslides are more vulnerable.  
  - Used as a binary factor (Yes/No) in this prototype.

These layers are combined into a **0–100 risk score**, then classified into Low/Medium/High.
"""
)

# -------------------------
# About & Scalability
# -------------------------
st.header("About A.R.P.H.A")

st.markdown(
    """
**A.R.P.H.A (Advanced Radar for Precipitation and Hazard Alerts)** is an early warning system for flash floods in hilly regions.

- **Current pilot:** Kullu–Manali–Mandi corridor, Himachal Pradesh.  
- **Core capability:** Multi-source risk assessment using rainfall, terrain (slope), soil moisture, and historical events.  
- **Data sources (design):**  
  - Rainfall: IMD stations, gridded rainfall, GPM/IMERG satellite.  
  - Terrain: DEM (SRTM/ALOS) for slope classification.  
  - Soil moisture: SMAP / ESA CCI.  
  - Historical events: NDMA / state disaster records.  

- **Future extension:**  
  - Add real-time data pipelines and ML-based models.  
  - Extend to upper Himachal (Lahaul & Spiti, Kinnaur) to classify rivers at risk from glacial spill / GLOF events.  
  - Integrate with SMS/WhatsApp/IVR for last-mile alerts.
"""
)