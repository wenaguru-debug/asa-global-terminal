import streamlit as st

# Institutional Branding
st.set_page_config(page_title="ASA GLOBAL", layout="wide")

if 'auth' not in st.session_state:
    st.session_state.auth = False

# Sidebar for Navigation
if st.session_state.auth:
    st.sidebar.title("🛠️ ASA CONTROL")
    menu = st.sidebar.radio("Navigation", ["DASHBOARD", "TACTICAL SYNC"])

# Login Gate
if not st.session_state.auth:
    st.title("🏛️ ASA GLOBAL INSTITUTIONAL")
    pwd = st.text_input("ENTER ACCESS KEY:", type="password")
    if st.button("LOGIN"):
        if pwd == "ASA_UNIVERSE_2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("INVALID KEY")
else:
    if menu == "DASHBOARD":
        st.header("📈 ASA GLOBAL TERMINAL")
        st.write("System Status: ONLINE")
        st.info("Awaiting tactical data feed...")
        
    elif menu == "TACTICAL SYNC":
        st.header("🛰️ VIDEO SYNC ENGINE")
        
        # TEST THE BRAIN
        try:
            from ultralytics import YOLO
            st.success("✅ AI ENGINE (YOLO) LOADED")
        except Exception as e:
            st.warning("⚠️ AI Engine still warming up or needs installation.")

        yt_url = st.text_input("PASTE TACTICAL YOUTUBE URL:")
        if yt_url:
            st.video(yt_url)
