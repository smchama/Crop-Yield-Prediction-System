# crop_yield_app.py
import os
import pickle
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

# -----------------------
# Header
# -----------------------
st.markdown("""
<div style="background-color:green; padding: 14px">
    <h1 style="color: white; text-align: center;">Crop Yield Prediction System</h1>
</div>
""", unsafe_allow_html=True)

# -----------------------
# Load Dataset
# -----------------------
@st.cache_data
def load_dataset():
    df = pd.read_csv("crop_data.csv")
    df.dropna(inplace=True)
    return df

train_df = load_dataset()

# -----------------------
# Crop Images
# -----------------------
crop_images = {
    "Maize": "images/maize.jpg",
    "Sorghum": "images/sorghum.jpg",
    "Cowpeas": "images/cowpeas.jpg",
    "Fruits": "images/fruits.jpg",
    "Millet": "images/millet.jpg",
    "Vegetables": "images/vegetables.jpg"
}

st.markdown("## Crop Types")
cols = st.columns(len(crop_images))
for idx, (crop_name, img_path) in enumerate(crop_images.items()):
    with cols[idx]:
        if os.path.exists(img_path):
            st.image(Image.open(img_path), use_container_width=True)
        else:
            st.text(f"{crop_name} image not found")

# -----------------------
# Model File & GitHub Release
# -----------------------
MODEL_FILE = "model.pkl"
VERSION_FILE = "model_version.txt"
GITHUB_API_LATEST_RELEASE = "https://api.github.com/repos/smchama/Crop-Yield-Prediction-System/releases/latest"

def download_latest_model_auto():
    st.info("Checking for latest model on GitHub...")
    with st.spinner("Fetching latest release info..."):
        try:
            response = requests.get(GITHUB_API_LATEST_RELEASE)
            response.raise_for_status()
        except:
            st.warning("Cannot reach GitHub. Using local model if available.")
            return False

        release_data = response.json()
        latest_version = release_data.get("tag_name", "")
        local_version = ""
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, "r") as f:
                local_version = f.read().strip()

        if latest_version != local_version:
            st.info(f"New model version detected: {latest_version}. Downloading...")
            assets = release_data.get("assets", [])
            for asset in assets:
                if asset["name"] == "model.pkl":
                    r = requests.get(asset["browser_download_url"])
                    if r.status_code == 200:
                        with open(MODEL_FILE, "wb") as f:
                            f.write(r.content)
                        with open(VERSION_FILE, "w") as f:
                            f.write(latest_version)
                        st.success(f"Model updated to version {latest_version}")
                        return True
        else:
            st.info("Local model is up to date.")
            return True
    return False

# -----------------------
# Train & Save Model
# -----------------------
def train_and_save_model():
    crop_dummies = pd.get_dummies(train_df['Crop_Name'])
    df = pd.concat([train_df, crop_dummies], axis=1)

    numeric_features = ['Rainfall','Humidity','Temperature','Pesticides','Soil_ph','N','P','K','Area_Planted']
    features = numeric_features + list(crop_dummies.columns)
    X = df[features]
    y = df['Total_production']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Scale numeric features
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    X_train_scaled[numeric_features] = scaler.fit_transform(X_train[numeric_features])
    X_test_scaled[numeric_features] = scaler.transform(X_test[numeric_features])

    # Train model
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)

    # Save model
    with open(MODEL_FILE, "wb") as f:
        pickle.dump({
            "model": model,
            "scaler": scaler,
            "numeric_features": numeric_features,
            "crop_columns": list(crop_dummies.columns)
        }, f)

    return model, scaler, numeric_features, list(crop_dummies.columns)

# -----------------------
# Load or Auto-Update Model
# -----------------------
if not os.path.exists(MODEL_FILE) or not download_latest_model_auto():
    st.warning("Training a new model locally...")
    model, scaler, numeric_features, crop_columns = train_and_save_model()
    st.success("Model trained and saved!")
else:
    with open(MODEL_FILE, "rb") as f:
        saved = pickle.load(f)
    model = saved["model"]
    scaler = saved["scaler"]
    numeric_features = saved["numeric_features"]
    crop_columns = saved["crop_columns"]

# -----------------------
# Tabs
# -----------------------
tab1, tab2, tab3, tab4 = st.tabs(["Predict", "Dataset", "Plots", "Comparison"])

# -----------------------
# Predict Tab
# -----------------------
with tab1:
    st.header("Yield Prediction")
    district = st.selectbox("Select District", ["Gwanda","Umzingwane","Insiza","Matobo","Beitbridge"])
    selected_crops = st.multiselect("Select Crop(s)", crop_columns, default=["Maize"])

    Rainfall = st.slider("Rainfall (MM)", 1, 1000, 100)
    Humidity = st.slider("Humidity (%)", 1, 100, 50)
    Temperature = st.slider("Temperature (°C)", 1, 50, 25)
    Pesticides = st.slider("Pesticides (Tonnes)", 1, 5000, 50)
    Soil_ph = st.slider("Soil PH", 1, 14, 6)
    N = st.slider("Nitrogen (kg)", 1, 500, 50)
    P = st.slider("Phosphorous (kg)", 1, 500, 30)
    K = st.slider("Potassium (kg)", 1, 500, 20)
    Area_Planted = st.slider("Area Planted (Hectares)", 1, 50000, 1000)

    if st.button("Predict"):
        threshold = 5
        st.session_state['results'] = {}
        for crop_name in selected_crops:
            crop_vector = [1 if crop_name == c else 0 for c in crop_columns]
            numeric_vector = [Rainfall, Humidity, Temperature, Pesticides, Soil_ph, N, P, K, Area_Planted]
            numeric_scaled = scaler.transform([numeric_vector])
            input_vector = list(numeric_scaled[0]) + crop_vector

            pred = model.predict([input_vector])[0]
            total_production = pred * Area_Planted
            yield_per_hectare = pred
            st.session_state['results'][crop_name] = (total_production, yield_per_hectare)

            # Display individual results
            st.subheader(f"{crop_name} Crop in {district} District")
            st.write(f"Total Production: {round(total_production,3)} tonnes")
            st.write(f"Yield per Hectare: {round(yield_per_hectare,3)} tonnes")

            if yield_per_hectare >= threshold:
                status = "HIGH"
                color = "green"
            else:
                status = "LOW"
                color = "#880808"

            st.markdown(
                f"<div style='background-color:{color}; padding:12px; color:white; text-align:center; "
                f"border-radius:5px; margin-bottom:15px'><b>Yield is {status}</b></div>",
                unsafe_allow_html=True
            )

# -----------------------
# Comparison Tab
# -----------------------
import plotly.graph_objects as go

# -----------------------
# Comparison Tab (Interactive)
# -----------------------
with tab4:
    st.header(" Crops Yield Comparison (Interactive)")
    if 'results' in st.session_state and st.session_state['results']:
        results = st.session_state['results']
        crop_names = list(results.keys())
        total_productions = [v[0] for v in results.values()]
        yields_per_hect = [v[1] for v in results.values()]
        colors = ["green" if y >= 5 else "#880808" for y in yields_per_hect]

        # Total Production Bar Chart
        fig_total = go.Figure()
        fig_total.add_trace(go.Bar(
            x=crop_names,
            y=total_productions,
            marker_color=colors,
            text=[f"{v:.2f} tonnes" for v in total_productions],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Total Production: %{y:.2f} tonnes<extra></extra>'
        ))
        fig_total.update_layout(title="Predicted Total Production per Crop",
                                xaxis_title="Crop", yaxis_title="Total Production (tonnes)")
        st.plotly_chart(fig_total, use_container_width=True)

        # Yield per Hectare Bar Chart
        fig_yield = go.Figure()
        fig_yield.add_trace(go.Bar(
            x=crop_names,
            y=yields_per_hect,
            marker_color=colors,
            text=[f"{v:.2f} tonnes/ha" for v in yields_per_hect],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Yield per Hectare: %{y:.2f} tonnes<extra></extra>'
        ))
        fig_yield.update_layout(title="Predicted Yield per Hectare per Crop",
                                xaxis_title="Crop", yaxis_title="Yield per Hectare (tonnes)")
        st.plotly_chart(fig_yield, use_container_width=True)
    else:
        st.info("Perform a prediction first to see comparison.")
        
        

# -----------------------
# Dataset Tab
# -----------------------
with tab2:
    st.header("Dataset Preview")
    st.dataframe(train_df.head())
    st.write(f"Dataset shape: {train_df.shape}")
    st.write("Columns:", train_df.columns.tolist())

# -----------------------
# Plots Tab
# -----------------------
with tab3:
    st.header("Data Visualizations")
    st.subheader("Histogram of Total Production")
    plt.figure(figsize=(10,5))
    plt.hist(train_df['Total_production'], bins=30, color='green', edgecolor='black')
    plt.xlabel('Total Production')
    plt.ylabel('Frequency')
    st.pyplot(plt)

    st.subheader("Scatter: Area Planted vs Total Production")
    plt.figure(figsize=(10,5))
    plt.scatter(train_df['Area_Planted'], train_df['Total_production'], color='blue')
    plt.xlabel('Area Planted')
    plt.ylabel('Total Production')
    st.pyplot(plt)

    st.subheader("Boxplot: Total Production per Crop")
    plt.figure(figsize=(12,6))
    sns.boxplot(x='Crop_Name', y='Total_production', data=train_df)
    plt.xticks(rotation=45)
    st.pyplot(plt)

    st.subheader("Correlation Heatmap")
    plt.figure(figsize=(10,8))
    corr = train_df[numeric_features + ['Total_production']].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    st.pyplot(plt)

# -----------------------
# Footer
# -----------------------
st.markdown("""
<div style="
    width: 100%;
    background-color: #e0e0e0;
    text-align: center;
    padding: 10px;
    font-size: 14px;
    color: black;
    margin-top: 20px;
">
    Developed by @ Chama Mthokozisi | BSEH | 2022
</div>
""", unsafe_allow_html=True)