import streamlit as st
import pandas as pd
import os
import torch

# --- 1. INSTITUTIONAL THEMING ---
st.set_page_config(page_title="ASA GLOBAL | TACTICAL TERMINAL", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0A0A0A; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #121212; border-right: 1px solid #333; }
    .stMetric { background-color: #1E1E1E; padding: 15px; border-radius: 5px; border: 1px solid #333; }
    div[data-testid="stMetricValue"] { color: #00FF00; font-family: 'Courier New', monospace; }
    h1, h2, h3 { color: #FFFFFF; font-family: 'Helvetica Neue', sans-serif; letter-spacing: -1px; }
    .stButton>button { background-color: #00FF00; color: black; font-weight: bold; border-radius: 2px; width: 100%; }
    .stTextInput>div>div>input { background-color: #1E1E1E; color: #00FF00; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🏛️ ASA GLOBAL INSTITUTIONAL ACCESS")
    col1, _ = st.columns([1, 2])
    with col1:
        pwd = st.text_input("TERMINAL_KEY >", type="password")
        if st.button("EXECUTE"):
            if pwd == "ASA_UNIVERSE_2026":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- 3. ENGINE CORE (RESILIENT LOADING) ---
@st.cache_resource
def get_engine():
    try:
        from ultralytics import YOLO
        # Master Key for PyTorch 2.6 security
        def patched_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return torch.original_load(*args, **kwargs)
        if not hasattr(torch, 'original_load'):
            torch.original_load = torch.load
            torch.load = patched_load
        return YOLO('yolov8n.pt')
    except Exception as e:
        return None

engine = get_engine()

# --- 4. SIDEBAR & NAVIGATION ---
st.sidebar.markdown("### 🛰️ SYSTEM STATUS: ONLINE")
menu = st.sidebar.radio("COMMAND_MENU", ["DASHBOARD", "TACTICAL_SYNC", "DATA_LAKE"])

# --- 5. MODULES ---
if menu == "DASHBOARD":
    st.title("📈 MARKET & TACTICAL OVERVIEW")
    c1, c2, c3 = st.columns(3)
    c1.metric("AI_LATENCY", "12ms", "+2ms")
    c2.metric("SYNC_STATUS", "OPTIMAL")
    c3.metric("TRACKED_NODES", "0", "AWAITING FEED")
    st.divider()
    st.code("[INFO] Connection established\n[INFO] AI Engine Loaded\n[INFO] Awaiting Feed...", language='bash')

elif menu == "TACTICAL_SYNC":
    st.title("🛰️ TACTICAL_SYNC_ENGINE")
    
    uploaded_file = st.file_uploader("UPLOAD TACTICAL WIDE-ANGLE FEED", type=['mp4', 'mov', 'avi'])
    
    if uploaded_file is not None:
        col_left, col_right = st.columns([3, 2])
        
        # Save temp file
        with open("temp_tactical_video.mp4", "wb") as f:
            f.write(uploaded_file.read())
            
        with col_left:
            st.video(uploaded_file)
            
        with col_right:
            st.subheader("AI_ANALYSIS_PULSE")
            if engine:
                st.success("✅ AI_CORE_ONLINE")
                
                if st.button("RUN TACTICAL FRAME ANALYSIS"):
                    with st.status("Processing Local Feed...", expanded=True) as status:
                        import cv2
                        
                        cap = cv2.VideoCapture("temp_tactical_video.mp4")
                        ret, frame = cap.read()
                        cap.release()
                        
                        if ret:
                            # THE FIX: This block must be indented inside 'if ret:'
                            st.write("Applying Wide-Angle Zoom (1280px)...")
                            results = engine(
                                frame, 
                                imgsz=1280,   # High-res for tiny players
                                conf=0.25,    # Sensitivity
                                classes=[0]   # '0' is the code for 'Person'
                            )
                            
                            annotated_frame = results[0].plot()
                            st.image(annotated_frame, caption="PROPRIETARY TACTICAL ANALYSIS", use_container_width=True)
                            
                            node_count = len(results[0].boxes)
                            st.metric("NODES_DETECTED", f"{node_count}")
                            status.update(label="ANALYSIS_COMPLETE", state="complete")
                        else:
                            st.error("Error: Could not read video frame.")
            else:
                st.error("❌ ENGINE_OFFLINE")
elif menu == "DATA_LAKE":
    st.title("📊 DATA_LAKE_SYNCHRONIZATION")
    sync_data = {
        'FRAME_ID': [100, 101, 102, 103, 104],
        'SEC_INDEX': [4.0, 4.04, 4.08, 4.12, 4.16],
        'PLAYER_X': [0.124, 0.125, 0.127, 0.130, 0.132],
        'PLAYER_Y': [0.880, 0.881, 0.882, 0.884, 0.885],
        'VELOCITY_M/S': [6.2, 6.3, 6.5, 6.8, 7.1]
    }
    df = pd.DataFrame(sync_data)
    st.dataframe(df, use_container_width=True)
    st.download_button("EXPORT_CSV", df.to_csv(), "asa_tactical_export.csv")
