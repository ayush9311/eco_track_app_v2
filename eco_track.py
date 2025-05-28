import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "cover"
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["eco_track_db"]
collection = db["emissions"]

# Cover Page
if st.session_state.page == "cover":
    st.image("forest.jpeg", use_column_width=True)
    st.title("🌍 Welcome to EcoTrack")
    st.markdown("""
    Carbon emissions are a leading cause of climate change. Our actions — from how we travel to the waste we produce — 
    all contribute to our carbon footprint.

    EcoTrack helps you calculate your personal carbon footprint and gives tips to reduce it, all while earning green rewards! 🌱
    """)
    if st.button("🚀 Calculate your carbon footprint"):
        st.session_state.page = "info"
        st.experimental_rerun()

# Info Page
elif st.session_state.page == "info":
    st.title("👤 Enter Your Information")
    name = st.text_input("Name")
    height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
    weight = st.number_input("Weight (kg)", min_value=20, max_value=200, value=70)
    if st.button("Next"):
        st.session_state.user_data["username"] = name
        st.session_state.user_data["height"] = height
        st.session_state.user_data["weight"] = weight
        st.session_state.page = "travel"
        st.experimental_rerun()

# Travel
elif st.session_state.page == "travel":
    st.title("🚗 Personal Travel")
    travel_km = st.slider("Travelled distance (km/week)", 0, 1000, 100)
    if st.button("Next: Waste"):
        st.session_state.user_data["travel_km"] = travel_km
        st.session_state.page = "waste"
        st.experimental_rerun()

# Waste
elif st.session_state.page == "waste":
    st.title("🗑️ Waste Generation")
    waste_kg = st.slider("Waste produced (kg/week)", 0, 100, 10)
    if st.button("Next: Energy"):
        st.session_state.user_data["waste_kg"] = waste_kg
        st.session_state.page = "energy"
        st.experimental_rerun()

# Energy
elif st.session_state.page == "energy":
    st.title("⚡ Energy Consumption")
    energy_kwh = st.slider("Electricity used (kWh/week)", 0, 500, 100)
    if st.button("Show My Carbon Emission"):
        st.session_state.user_data["energy_kwh"] = energy_kwh
        st.session_state.page = "result"
        st.experimental_rerun()

# Result Page
elif st.session_state.page == "result":
    data = st.session_state.user_data

    # Emission Factors
    CO2_per_km = 0.21
    CO2_per_kg_waste = 1.2
    CO2_per_kwh = 0.5

    # Calculations
    travel_emission = data["travel_km"] * CO2_per_km
    waste_emission = data["waste_kg"] * CO2_per_kg_waste
    energy_emission = data["energy_kwh"] * CO2_per_kwh
    total_emission = travel_emission + waste_emission + energy_emission
    trees_needed = total_emission / 21

    # Store in DB
    record = {
        "username": data["username"],
        "date": datetime.now(),
        "height_cm": data["height"],
        "weight_kg": data["weight"],
        "travel_km": data["travel_km"],
        "waste_kg": data["waste_kg"],
        "energy_kwh": data["energy_kwh"],
        "total_emission": total_emission,
        "trees_needed": trees_needed
    }
    collection.insert_one(record)

    # Display results
    st.title("🌡️ Your Carbon Emission Report")
    st.metric("Total CO₂ Emissions", f"{total_emission:.2f} kg")
    st.write(f"🌳 Trees needed to offset this: **{trees_needed:.1f} trees**")

    # Tips
    st.subheader("💡 Tips to Reduce Emissions")
    if data["travel_km"] > 200:
        st.info("🚲 Try using public transport or cycling for short trips.")
    if data["waste_kg"] > 50:
        st.info("♻️ Reduce, reuse, recycle to manage your waste.")
    if data["energy_kwh"] > 200:
        st.info("🔌 Turn off appliances when not in use and use energy-efficient ones.")
    if data["travel_km"] <= 200 and data["waste_kg"] <= 50 and data["energy_kwh"] <= 200:
        st.success("✅ You're doing great! Keep it up.")

    # Rewards
    st.subheader("🏅 Eco Rewards")
    if total_emission < 50:
        st.success("🏆 Green Hero: You earn the **Eco Warrior** badge!")
    elif total_emission < 100:
        st.info("🥈 Good Effort: You earn the **Green Guardian** badge!")
    elif total_emission < 200:
        st.warning("🌿 Keep Going: You earn the **Eco Explorer** badge!")
    else:
        st.error("💡 Try reducing your carbon habits to earn a badge.")

    # Leaderboard
    st.subheader("📊 Leaderboard")
    top_users = list(collection.find().sort("total_emission", 1).limit(5))
    if top_users:
        df = pd.DataFrame({
            "Username": [u["username"] for u in top_users],
            "CO₂ (kg)": [round(u["total_emission"], 2) for u in top_users]
        })
        st.table(df)
    else:
        st.write("No entries yet. Be the first eco champion!")
# Show team button only on the cover page
if st.session_state.page == "cover":
    with st.container():
        st.markdown("""
            <style>
            .footer {
                position: fixed;
                bottom: 10px;
                width: 100%;
                text-align: center;
                color: gray;
                font-size: 14px;
            }
            </style>
            <div class="footer">
                <hr style='border: none; border-top: 1px solid gray; width: 60%; margin: auto;'/>
            </div>
        """, unsafe_allow_html=True)

        with st.expander("👥 Team Members"):
            st.write("Ayush Kumar Singh")
            st.write("Amishi Senger")
            st.write("Himanshi Sharma")
