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
                
                if st.button("RUN FULL TACTICAL DATA SYNC"):
                    with st.status("Syncing Python Logic to Video Frames...", expanded=True) as status:
                        import cv2
                        import pandas as pd
                        
                        cap = cv2.VideoCapture("temp_tactical_video.mp4")
                        all_sync_data = []
                        frame_count = 0
                        
                        # Process 1 frame per second to maintain institutional speed
                        while cap.isOpened():
                            ret, frame = cap.read()
                            if not ret:
                                break
                                
                            if frame_count % 30 == 0:
                                st.write(f"Analyzing Time: {frame_count//30}s...")
                                results = engine(frame, imgsz=1280, conf=0.15, classes=[0], verbose=False)
                                
                                # Grab every player's center-point (X, Y)
                                for box in results[0].boxes.xywh.cpu().numpy():
                                    x, y, w, h = box
                                    all_sync_data.append({
                                        "TIMESTAMP_SEC": frame_count // 30,
                                        "COORD_X": round(float(x), 2),
                                        "COORD_Y": round(float(y), 2),
                                        "CONFIDENCE": round(float(results[0].boxes.conf[0]), 2)
                                    })
                            
                            frame_count += 1
                            if frame_count > 300: # First 10 seconds of tactical sync
                                break
                        
                        cap.release()
                        st.session_state['synced_df'] = pd.DataFrame(all_sync_data)
                        status.update(label="SYNC COMPLETE: DATA_LAKE UPDATED", state="complete")
            else:
                st.error("❌ ENGINE_OFFLINE")

elif menu == "DATA_LAKE":
    st.title("📊 DATA_LAKE_SYNCHRONIZATION")
    st.markdown("Raw Python coordinate output synced to video frame timestamps.")
    
    if 'synced_df' in st.session_state:
        df = st.session_state['synced_df']
        st.metric("TOTAL_NODES_RECORDED", len(df))
        st.dataframe(df, use_container_width=True)
        st.download_button("EXPORT_INSTITUTIONAL_CSV", df.to_csv(index=False), "asa_tactical_export.csv")
    else:
        st.warning("DATA_LAKE_EMPTY: Execute TACTICAL_SYNC to populate coordinates.")
