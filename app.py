import streamlit as st
import pandas as pd
import numpy as np
import os
import torch
import cv2

# --- 1. SYSTEM CONFIG & ARCHITECTURE ---
st.set_page_config(page_title="ASA GLOBAL | TACTICAL TERMINAL", layout="wide")

# Institutional Styling
st.markdown("""
    <style>
    .stApp { background-color: #0A0A0A; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #121212; border-right: 1px solid #333; }
    .stMetric { background-color: #1E1E1E; padding: 15px; border-radius: 5px; border: 1px solid #333; }
    div[data-testid="stMetricValue"] { color: #00FF00; font-family: 'Courier New', monospace; }
    .stButton>button { background-color: #00FF00; color: black; font-weight: bold; border-radius: 2px; }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session Memory
if 'synced_df' not in st.session_state:
    st.session_state['synced_df'] = None
if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- 2. SECURITY GATE ---
if not st.session_state.auth:
    st.title("🏛️ ASA GLOBAL INSTITUTIONAL ACCESS")
    pwd = st.text_input("TERMINAL_KEY >", type="password")
    if st.button("EXECUTE"):
        if pwd == "ASA_UNIVERSE_2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. PRODUCTION ENGINE (WITH TRACKING) ---
@st.cache_resource
def get_engine():
    try:
        from ultralytics import YOLO
        # PyTorch 2.6 Patch
        def patched_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return torch.original_load(*args, **kwargs)
        if not hasattr(torch, 'original_load'):
            torch.original_load = torch.load
            torch.load = patched_load
        return YOLO('yolov8n.pt')
    except Exception:
        return None

engine = get_engine()

# --- 4. NAVIGATION ---
menu = st.sidebar.radio("COMMAND_MENU", ["DASHBOARD", "TACTICAL_SYNC", "DATA_LAKE"])

# --- 5. TACTICAL SYNC (THE PRODUCTION LOOP) ---
if menu == "TACTICAL_SYNC":
    st.title("🛰️ TACTICAL_SYNC_ENGINE")
    uploaded_file = st.file_uploader("UPLOAD FEED", type=['mp4', 'mov', 'avi'])
    
    if uploaded_file:
        t_col1, t_col2 = st.columns([3, 2])
        with open("temp_v.mp4", "wb") as f: f.write(uploaded_file.read())
        
        with t_col1:
            st.video(uploaded_file)
            
        with t_col2:
            if st.button("RUN INSTITUTIONAL DATA SYNC"):
                with st.status("Processing Tactical Metadata...", expanded=True) as status:
                    cap = cv2.VideoCapture("temp_v.mp4")
                    data_points = []
                    f_idx = 0
                    
                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret or f_idx > 300: break # Process 10s for speed
                        
                        if f_idx % 30 == 0:
                            # Using TRACK instead of PREDICT for IDs
                            results = engine.track(frame, persist=True, imgsz=1280, conf=0.15, classes=[0], verbose=False)
                            
                            if results[0].boxes.id is not None:
                                boxes = results[0].boxes.xywh.cpu().numpy()
                                ids = results[0].boxes.id.cpu().numpy().astype(int)
                                for box, obj_id in zip(boxes, ids):
                                    data_points.append({
                                        "SEC": f_idx // 30,
                                        "ID": obj_id,
                                        "X": round(float(box[0]), 1),
                                        "Y": round(float(box[1]), 1)
                                    })
                        f_idx += 1
                    cap.release()
                    st.session_state['synced_df'] = pd.DataFrame(data_points)
                    status.update(label="SYNC COMPLETE", state="complete")

# --- 6. DATA LAKE (THE ANALYST SUITE) ---
elif menu == "DATA_LAKE":
    st.title("📊 DATA_LAKE_SYNCHRONIZATION")
    
    if st.session_state['synced_df'] is not None:
        df = st.session_state['synced_df']
        
        # SAFETY CHECK: Ensure the new 'ID' column exists before plotting
        if 'ID' in df.columns:
            # PRODUCTION METRICS
            m1, m2 = st.columns(2)
            m1.metric("UNIQUE_PLAYERS", len(df['ID'].unique()))
            m2.metric("DATA_NODES", len(df))
            
            # 3. TACTICAL HEATMAP (The Professional View)
        st.divider()
        st.subheader("🛰️ TACTICAL DENSITY HEATMAP")
        
        import seaborn as sns
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#0A0A0A')
        ax.set_facecolor('#121212')

        # Create the heatmap based on X and Y coordinates
        sns.kdeplot(
            data=df, x="X", y="Y", 
            fill=True, thresh=0, levels=10, cmap="viridis", alpha=0.6, ax=ax
        )
        
        ax.set_title("PLAYER_ZONE_DOMINANCE", color='white', loc='left')
        ax.axis('off') # Clean tactical look
        st.pyplot(fig)
            
            # TACTICAL SUMMARY
            st.subheader("PLAYER_ACTIVITY_SUMMARY")
            # Grouping by ID to see how many seconds each player was tracked
            summary = df.groupby('ID').agg({
                'SEC': 'count',
                'X': ['mean', 'std'],
                'Y': ['mean', 'std']
            })
            st.dataframe(summary, use_container_width=True)
        else:
            st.warning("⚠️ OLD DATA DETECTED: The Data Lake contains legacy coordinates without Tracking IDs.")
            if st.button("PURGE CACHE & RE-SYNC"):
                st.session_state['synced_df'] = None
                st.rerun()
        
        # RAW DATA & EXPORT
        with st.expander("VIEW_RAW_COORDINATE_LOG"):
            st.dataframe(df, use_container_width=True)
            st.download_button("EXPORT_CSV", df.to_csv(index=False), "tactical_data.csv")
    else:
        st.info("SYSTEM_AWAITING_DATA: Please go to TACTICAL_SYNC and run the analysis.")

# --- 7. DASHBOARD (SYSTEM HEALTH) ---
elif menu == "DASHBOARD":
    st.title("📈 SYSTEM_OVERVIEW")
    st.write("Terminal running on ASA_GLOBAL_CORE_v1.3")
    if engine: st.success("AI_ENGINE: ONLINE")
    if st.session_state['synced_df'] is not None:
        st.info(f"CACHE: {len(st.session_state['synced_df'])} nodes in memory.")
