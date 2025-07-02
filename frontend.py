
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
road_df = pd.read_csv("F:/Six_Months_Project/Web_app/sorted_15_days_data (1).csv")
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
        # next_hour_dt = current_dt.replace(second=0, microsecond=0) + timedelta(hours=1)
        # Generate next 24 hourly timestamps
        future_datetimes = [current_dt.replace(second=0, microsecond=0) + timedelta(hours=i+1) for i in range(24)]

        
        st.markdown(f"🕒 **Current Time:** `{current_dt.strftime('%Y-%m-%d %H:%M')}`")
        st.markdown(f"⏩ **Predicting from:** `{future_datetimes[0].strftime('%Y-%m-%d %H:%M')}` to `{future_datetimes[-1].strftime('%Y-%m-%d %H:%M')}`")
        
        # Use next_hour_dt for prediction
        selected_datetime = future_datetimes


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

# # ---------- Submit ----------
# st.markdown("## 🚀 Predict Next-Hour Speed")
# if st.button("🔍 Get Prediction", use_container_width=True):
#     input_data = {
#         'temp': temp,
#         'humidity': humidity,
#         'windspeed': wind_speed,
#         'Length': road_length,
#         'hour': selected_datetime.hour,
#         'dayofweek': selected_datetime.weekday(),
#         'icon': weather.lower().replace(" ", "-")
#     }

#     try:
#         response = requests.post("http://127.0.0.1:5000/predict", json=input_data)
#         if response.status_code == 200:
#             result = response.json()
#             speed = result['predicted_avg_speed']

#             # Traffic Interpretation
#             if speed >= 40:
#                 traffic_status = "🚗 No Traffic"
#                 color = [0, 200, 0]
#                 badge = "✅"
#             elif speed >= 30:
#                 traffic_status = "🟢 Low Traffic"
#                 color = [100, 255, 100]
#                 badge = "🟢"
#             elif speed >= 20:
#                 traffic_status = "🟠 Moderate Traffic"
#                 color = [255, 165, 0]
#                 badge = "🟠"
#             elif speed >= 10:
#                 traffic_status = "🔴 High Traffic"
#                 color = [255, 0, 0]
#                 badge = "🔴"
#             else:
#                 traffic_status = "🚨 Very High Traffic"
#                 color = [128, 0, 0]
#                 badge = "🚨"

#             # Show Prediction
#             st.success(f"{badge} **Predicted Speed on {selected_street}: {speed:.2f} km/h**")
#             st.info(f"**Traffic Condition**: {traffic_status}")

#             # Map Visualization
#             road_subset = road_subset.sort_values(by='Id')
#             line_data = pd.DataFrame([{
#                 "path": road_subset[['Long', 'Lat']].values.tolist(),
#                 "color": color
#             }])

#             layer = pdk.Layer(
#                 "PathLayer",
#                 data=line_data,
#                 get_path="path",
#                 get_color="color",
#                 width_scale=10,
#                 width_min_pixels=2,
#                 pickable=True
#             )

#             view_state = pdk.ViewState(
#                 latitude=lat,
#                 longitude=lon,
#                 zoom=15,
#                 pitch=0
#             )

#             st.markdown("### 🗺️ Traffic Visualization")
#             st.pydeck_chart(pdk.Deck(
#                 layers=[layer],
#                 initial_view_state=view_state,
#                 map_style="mapbox://styles/mapbox/navigation-night-v1"  # traffic style
#             ))
# ---------- Submit: 24-Hour Prediction ----------
st.markdown("## 🚀 Predict Speed for Next 24 Hours")

if st.button("🔍 Get 24-Hour Predictions", use_container_width=True):
    future_datetimes = [datetime.now().replace(second=0, microsecond=0) + timedelta(hours=i+1) for i in range(24)]
    predictions = []
    color_map = []

    try:
        for future_time in future_datetimes:
            input_data = {
                'temp': temp,
                'humidity': humidity,
                'windspeed': wind_speed,
                'Length': road_length,
                'hour': future_time.hour,
                'dayofweek': future_time.weekday(),
                'icon': weather.lower().replace(" ", "-")
            }

            response = requests.post("http://127.0.0.1:5000/predict", json=input_data)
            if response.status_code == 200:
                result = response.json()
                speed = result['predicted_avg_speed']

                # Traffic Category
                if speed >= 40:
                    status = "No Traffic 🚗"
                    color = [0, 200, 0]
                elif speed >= 30:
                    status = "Low Traffic 🟢"
                    color = [100, 255, 100]
                elif speed >= 20:
                    status = "Moderate Traffic 🟠"
                    color = [255, 165, 0]
                elif speed >= 10:
                    status = "High Traffic 🔴"
                    color = [255, 0, 0]
                else:
                    status = "Very High Traffic 🚨"
                    color = [128, 0, 0]

                predictions.append({
                    "Time": future_time.strftime('%Y-%m-%d %H:%M'),
                    "Predicted Speed (km/h)": round(speed, 2),
                    "Traffic Condition": status
                })
                color_map.append(color)
            else:
                predictions.append({
                    "Time": future_time.strftime('%Y-%m-%d %H:%M'),
                    "Predicted Speed (km/h)": "Failed",
                    "Traffic Condition": "Error"
                })
                color_map.append([128, 128, 128])  # Grey for error

        # Convert to DataFrame
        pred_df = pd.DataFrame(predictions)

        # ---------- Table Output ----------
        st.markdown("### 📋 Prediction Table")
        st.dataframe(pred_df, use_container_width=True)

        # ---------- Chart Output ----------
        st.markdown("### 📈 Predicted Speed Trend")
        chart_df = pred_df[pd.to_numeric(pred_df["Predicted Speed (km/h)"], errors='coerce').notnull()]
        chart_df["Predicted Speed (km/h)"] = chart_df["Predicted Speed (km/h)"].astype(float)
        st.line_chart(chart_df.set_index("Time")["Predicted Speed (km/h)"])

        # ---------- Map Output ----------
        st.markdown("### 🗺️ Traffic Route Visualization")

        # Use average color for now (last time's color)
        avg_color = color_map[-1] if color_map else [100, 100, 100]

        road_subset = road_subset.sort_values(by='Id')
        line_data = pd.DataFrame([{
            "path": road_subset[['Long', 'Lat']].values.tolist(),
            "color": avg_color
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

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/navigation-night-v1"
        ))

    except requests.exceptions.ConnectionError:
        st.error("❌ Backend server not running. Please start your Flask API.")


# ---------- Footer ----------
st.markdown("---")
st.caption("🚧 Developed for passengers & planners | Smart Traffic Forecast • 2025 ©")
