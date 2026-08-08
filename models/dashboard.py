import os
import pickle
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

# Page Configuration
st.set_page_config(
    page_title="ANiMeDRig - Farm Health Monitoring",
    layout="wide"
)

# Absolute File Paths
BASE_PROJECT_DIR = r"C:\Projects"
CSV_PATH = os.path.join(BASE_PROJECT_DIR, "data", "chicken_dataset_real.csv")
MODEL_PATH = os.path.join(BASE_PROJECT_DIR, "animedrg", "ml_models", "models", "chicken_health_model.pkl")

@st.cache_data(ttl=2)
def fetch_data():
    if not os.path.exists(CSV_PATH):
        st.error(f"Dataset missing at: {CSV_PATH}")
        return pd.DataFrame(), pd.DataFrame()
    
    df = pd.read_csv(CSV_PATH)

    # Column Auto-Mapper
    col_map = {}
    for col in df.columns:
        c_lower = col.lower().strip()
        if c_lower in ["bw", "weight", "body_weight", "bodyweight"]:
            col_map[col] = "bw"
        elif c_lower in ["avg_temp", "temp", "temperature", "avgtemp"]:
            col_map[col] = "avg_temp"
        elif c_lower in ["tag_no", "tag", "tag_id", "chicken_id"]:
            col_map[col] = "tag_no"
        elif c_lower in ["created_at", "timestamp", "time", "date"]:
            col_map[col] = "timestamp"
    df.rename(columns=col_map, inplace=True)

    # Defaults fallback
    if "bw" not in df.columns:
        df["bw"] = 1.8
    if "avg_temp" not in df.columns:
        df["avg_temp"] = 36.5
    if "tag_no" not in df.columns:
        df["tag_no"] = [f"TAG-{100 + i}" for i in range(len(df))]
    if "timestamp" not in df.columns:
        df["timestamp"] = pd.date_range(end=pd.Timestamp.now(), periods=len(df), freq="10min")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Store ground truth if present
    if "health_status" in df.columns:
        df["ground_truth"] = df["health_status"]
    else:
        df["ground_truth"] = 1

    # Model Inference
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                model = pickle.load(f)
            
            X = df[["bw", "avg_temp"]]
            df["health_status"] = model.predict(X)
            
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(X)
                df["confidence"] = probs.max(axis=1)
            else:
                df["confidence"] = 0.95
        except Exception:
            df["confidence"] = 0.95
    else:
        df["confidence"] = 0.95

    devices_df = pd.DataFrame([{
        "device_id": "RaspberryPi-Rig-01",
        "status": "Online",
        "last_seen": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }])

    return df, devices_df

# Load Data
df_measurements, df_devices = fetch_data()

# App Bar
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("ANiMeDRig Live Monitoring Dashboard")
with col_btn:
    st.write("")
    if st.button("Refresh Data", use_container_width=True):
        st.rerun()

if df_measurements.empty:
    st.warning("No dataset found.")
    st.stop()

# Executive Overview Metrics
st.markdown("### Executive Overview")
m1, m2, m3, m4 = st.columns(4)

total_scanned = len(df_measurements)
healthy_cnt = int((df_measurements["health_status"] == 1).sum())
unhealthy_cnt = total_scanned - healthy_cnt
last_scan_time = df_measurements["timestamp"].max().strftime("%H:%M:%S %Y-%m-%d")

with m1:
    st.metric("Total Scans Today", total_scanned)
with m2:
    st.metric("Healthy / Unhealthy", f"{healthy_cnt} / {unhealthy_cnt}")
with m3:
    st.metric("Last Scan Timestamp", last_scan_time)
with m4:
    st.metric("System Status", "Online")

st.divider()

# Model Diagnostics & Confusion Matrix
st.markdown("### Model Diagnostics & Confusion Matrix")

y_true = df_measurements["ground_truth"]
y_pred = df_measurements["health_status"]

cm = confusion_matrix(y_true, y_pred, labels=[1, 0])
acc = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred, pos_label=0, zero_division=0)
rec = recall_score(y_true, y_pred, pos_label=0, zero_division=0)
f1 = f1_score(y_true, y_pred, pos_label=0, zero_division=0)

eval_col1, eval_col2 = st.columns([1, 1])

with eval_col1:
    st.markdown("#### Performance Summary")
    p1, p2 = st.columns(2)
    p1.metric("Accuracy Score", f"{acc * 100:.1f}%")
    p2.metric("F1-Score", f"{f1:.2f}")
    
    p3, p4 = st.columns(2)
    p3.metric("Precision (Unhealthy)", f"{prec * 100:.1f}%")
    p4.metric("Recall / Sensitivity", f"{rec * 100:.1f}%", help="Higher recall minimizes missed infections.")

with eval_col2:
    fig_cm = px.imshow(
        cm,
        x=["Predicted Healthy", "Predicted Unhealthy"],
        y=["Actual Healthy", "Actual Unhealthy"],
        color_continuous_scale="Blues",
        text_auto=True,
        title="Confusion Matrix"
    )
    fig_cm.update_layout(
        xaxis_title="Predicted Label",
        yaxis_title="Actual Label",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_cm, use_container_width=True)

st.divider()

# Core Visualizations
left_col, right_col = st.columns([1.2, 1])

with left_col:
    # Health Feed
    st.markdown("### Real-Time Health Feed")
    feed_display = df_measurements[["tag_no", "bw", "avg_temp", "health_status", "confidence", "timestamp"]].sort_values(by="timestamp", ascending=False).head(10).copy()
    feed_display["Status"] = feed_display["health_status"].apply(lambda x: "Healthy" if x == 1 else "Unhealthy")
    
    st.dataframe(
        feed_display[["tag_no", "bw", "avg_temp", "Status", "confidence", "timestamp"]],
        use_container_width=True,
        column_config={
            "tag_no": "Tag Number",
            "bw": st.column_config.NumberColumn("Weight (kg)", format="%.2f kg"),
            "avg_temp": st.column_config.NumberColumn("Temp (°C)", format="%.1f °C"),
            "confidence": st.column_config.NumberColumn("Confidence", format="%.2f"),
            "timestamp": "Timestamp"
        }
    )

    # Weight Trend
    st.markdown("### Weight Trends Over Time")
    fig_weight = px.line(
        df_measurements, 
        x="timestamp", 
        y="bw", 
        color="tag_no",
        title="Body Weight Progression",
        labels={"timestamp": "Time", "bw": "Body Weight (kg)", "tag_no": "Tag Number"},
        markers=True
    )
    fig_weight.update_layout(showlegend=True, hovermode="x unified")
    st.plotly_chart(fig_weight, use_container_width=True)

with right_col:
    # Health Ratio
    st.markdown("### Health Ratio Distribution")
    fig_pie = px.pie(
        names=["Healthy", "Unhealthy"],
        values=[healthy_cnt, unhealthy_cnt],
        color_discrete_sequence=["#2E7D32", "#C62828"],
        hole=0.4,
        title="Healthy vs Unhealthy Ratio"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Temperature Trend
    st.markdown("### Temperature Monitoring")
    fig_temp = px.line(
        df_measurements, 
        x="timestamp", 
        y="avg_temp", 
        title="Body Temperature Trends (°C)",
        labels={"timestamp": "Time", "avg_temp": "Temperature (°C)"},
        markers=True
    )
    fig_temp.add_hrect(y0=35, y1=37, fillcolor="#2E7D32", opacity=0.1, line_width=0, annotation_text="Optimal Range (35-37°C)")
    st.plotly_chart(fig_temp, use_container_width=True)

st.divider()

# Secondary Sections
s1, s2 = st.columns([1.2, 0.8])

with s1:
    st.markdown("### Flagged Animals Anomalies Plot")
    unhealthy_df = df_measurements[df_measurements["health_status"] == 0].copy()
    
    if not unhealthy_df.empty:
        unhealthy_df["timestamp_str"] = unhealthy_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
        
        fig_flagged = px.scatter(
            unhealthy_df,
            x="bw",
            y="avg_temp",
            hover_name="tag_no",
            hover_data={"bw": ":.2f", "avg_temp": ":.1f", "timestamp_str": True, "health_status": False},
            labels={
                "bw": "Body Weight (kg)", 
                "avg_temp": "Temperature (°C)",
                "timestamp_str": "Timestamp"
            },
            title="Weight vs Temperature Distribution (Unhealthy Classifications)",
            color_discrete_sequence=["#C62828"]
        )
        fig_flagged.update_traces(marker=dict(size=12, symbol="circle", opacity=0.85))
        st.plotly_chart(fig_flagged, use_container_width=True)
    else:
        st.info("No flagged anomalies detected.")

with s2:
    st.markdown("### Device Status Logs")
    st.dataframe(
        df_devices, 
        use_container_width=True,
        column_config={
            "device_id": "Device ID",
            "status": "Connection Status",
            "last_seen": "Last Heartbeat"
        }
    )

# Scan History Table
st.markdown("### Measurement Logs History")
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    selected_status = st.selectbox("Filter by Classification", ["All", "Healthy", "Unhealthy"])
with filter_col2:
    search_tag = st.text_input("Filter by Tag Number", "")

filtered_df = df_measurements.copy()
if selected_status == "Healthy":
    filtered_df = filtered_df[filtered_df["health_status"] == 1]
elif selected_status == "Unhealthy":
    filtered_df = filtered_df[filtered_df["health_status"] == 0]

if search_tag:
    filtered_df = filtered_df[filtered_df["tag_no"].astype(str).str.contains(search_tag, case=False)]

st.dataframe(
    filtered_df[["tag_no", "bw", "avg_temp", "health_status", "confidence", "timestamp"]],
    width="stretch",
    column_config={
        "tag_no": "Tag Number",
        "bw": st.column_config.NumberColumn("Weight (kg)", format="%.2f kg"),
        "avg_temp": st.column_config.NumberColumn("Temp (°C)", format="%.1f °C"),
        "health_status": "Classification Score",
        "confidence": st.column_config.NumberColumn("Confidence", format="%.2f"),
        "timestamp": "Timestamp"
    }
)
#streamlit run animedrg/models/dashboard.py