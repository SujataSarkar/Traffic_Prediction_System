
import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
from datetime import datetime

# ---------- Global Config ----------
pdk.settings.mapbox_api_key = "pk.eyJ1Ijoic3VqYXRhc2Fya2FyIiwiYSI6ImNtY2MycW9jMjAyZWoybHNhM3FzYmZ0NngifQ.VL6KfnlDlCg-n57T1K4J0g"
st.set_page_config(page_title="🚦 Traffic Speed Predictor", layout="wide")

# ---------- Title Section ----------
st.markdown("<h1 style='text-align:center; color:#1f77b4;'>🚦 Urban Traffic Speed Prediction</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px;'>Plan your journey smarter with real-time road speed estimation 🚘</p>", unsafe_allow_html=True)
st.markdown("---")

# ---------- Load Data ----------
road_df = pd.read_csv("sorted_15_days_data (1).csv")
road_df = road_df.dropna(subset=['Lat', 'Long', 'StreetName'])

# ---------- Selection Section ----------
from datetime import timedelta

with st.container():
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("🛣️ Choose Road Segment")
        unique_streets = road_df['StreetName'].dropna().unique()
        selected_street = st.selectbox("Select a road", sorted(unique_streets))
    
    with col2:
        st.subheader("⏱️ Prediction Time Info")
        
        # Get current datetime
        current_dt = datetime.now()
        next_hour_dt = current_dt.replace(second=0, microsecond=0) + timedelta(hours=1)
        
        st.markdown(f"🕒 **Current Time:** `{current_dt.strftime('%Y-%m-%d %H:%M')}`")
        st.markdown(f"⏩ **Predicting for:** `{next_hour_dt.strftime('%Y-%m-%d %H:%M')}`")
        
        # Use next_hour_dt for prediction
        selected_datetime = next_hour_dt


# ---------- Filter Selected Street ----------
road_subset = road_df[road_df['StreetName'] == selected_street]
if road_subset.empty:
    st.error("No data found for the selected road.")
    st.stop()

lat = road_subset['Lat'].mean()
lon = road_subset['Long'].mean()
road_length = round(road_subset['Length'].mean(), 2) if 'Length' in road_df.columns else 1.0

# ---------- Inputs ----------
st.markdown("### 🌡️ Enter Current Road & Weather Conditions")

col1, col2 = st.columns(2)
with col1:
    temp = st.slider("🌡️ Temperature (°C)", -10.0, 50.0, 28.0, 0.5)
    humidity = st.slider("💧 Humidity (%)", 0.0, 100.0, 60.0, 1.0)
    weekend = st.radio("🗓️ Is it Weekend?", ["No", "Yes"], horizontal=True)

with col2:
    wind_speed = st.slider("💨 Wind Speed (km/h)", 0.0, 100.0, 10.0, 0.5)
    weather = st.selectbox("⛅ Weather Condition", ["Clear", "Cloudy", "Rainy", "Storm"])

# Encode Inputs
weekend_flag = 1 if weekend == "Yes" else 0

# ---------- Submit ----------
st.markdown("## 🚀 Predict Next-Hour Speed")
if st.button("🔍 Get Prediction", use_container_width=True):
    input_data = {
        'temp': temp,
        'humidity': humidity,
        'windspeed': wind_speed,
        'Length': road_length,
        'hour': selected_datetime.hour,
        'dayofweek': selected_datetime.weekday(),
        'icon': weather.lower().replace(" ", "-")
    }

    try:
        response = requests.post("https://dynamic-victory-production.up.railway.app/", json=input_data)
        if response.status_code == 200:
            result = response.json()
            speed = result['predicted_avg_speed']

            # Traffic Interpretation
            if speed >= 40:
                traffic_status = "🚗 No Traffic"
                color = [0, 200, 0]
                badge = "✅"
            elif speed >= 30:
                traffic_status = "🟢 Low Traffic"
                color = [100, 255, 100]
                badge = "🟢"
            elif speed >= 20:
                traffic_status = "🟠 Moderate Traffic"
                color = [255, 165, 0]
                badge = "🟠"
            elif speed >= 10:
                traffic_status = "🔴 High Traffic"
                color = [255, 0, 0]
                badge = "🔴"
            else:
                traffic_status = "🚨 Very High Traffic"
                color = [128, 0, 0]
                badge = "🚨"

            # Show Prediction
            st.success(f"{badge} **Predicted Speed on {selected_street}: {speed:.2f} km/h**")
            st.info(f"**Traffic Condition**: {traffic_status}")

            # Map Visualization
            road_subset = road_subset.sort_values(by='Id')
            line_data = pd.DataFrame([{
                "path": road_subset[['Long', 'Lat']].values.tolist(),
                "color": color
            }])

            layer = pdk.Layer(
                "PathLayer",
                data=line_data,
                get_path="path",
                get_color="color",
                width_scale=10,
                width_min_pixels=2,
                pickable=True
            )

            view_state = pdk.ViewState(
                latitude=lat,
                longitude=lon,
                zoom=15,
                pitch=0
            )

            st.markdown("### 🗺️ Traffic Visualization")
            st.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                map_style="mapbox://styles/mapbox/navigation-night-v1"  # traffic style
            ))

        else:
            st.error("❌ Prediction failed. Please try again.")
    except requests.exceptions.ConnectionError:
        st.error("❌ Backend server not running. Please start your Flask API.")

# ---------- Footer ----------
st.markdown("---")
st.caption("🚧 Developed for passengers & planners | Smart Traffic Forecast • 2025 ©")
