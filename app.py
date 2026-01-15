import streamlit as st
import pandas as pd
import numpy as np
from ultralytics import YOLO
import cv2
import tempfile
from fpdf import FPDF
import datetime
import os

# --- CLASS 1: THE PDF ARCHITECT ---
class ASAReport(FPDF):
    def header(self):
        # Professional Institutional Header
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'ASA GLOBAL - INSTITUTIONAL MATCH DOSSIER', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, f" {title}", 0, 1, 'L', 1)
        self.ln(4)

    def add_metric_row(self, label, value):
        self.set_font('Arial', '', 10)
        self.cell(100, 8, label, 1)
        self.cell(0, 8, str(value), 1, 1)

# --- CLASS 2: THE ASA CORE ENGINE ---
class ASAGlobalCore:
    def __init__(self, model_variant='yolov8n.pt'):
        self.model = YOLO(model_variant)
        self.pitch_length = 105.0
        self.pitch_width = 68.0

    def process_match_stream(self, video_source, sampling_rate=0.5):
        """
        Memory-optimized streaming for full matches.
        sampling_rate: Seconds between analysis (0.5 = 2fps)
        """
        cap = cv2.VideoCapture(video_source)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_stride = int(fps * sampling_rate)
        
        match_data = []
        frame_idx = 0
        
        # Progress Bar for Streamlit UI
        prog_bar = st.progress(0)
        status_text = st.empty()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            if frame_idx % frame_stride == 0:
                # Optimized inference
                results = self.model.track(frame, persist=True, verbose=False, conf=0.35, classes=[0])
                
                if results[0].boxes.id is not None:
                    h, w, _ = frame.shape
                    boxes = results[0].boxes.xywh.cpu().numpy()
                    ids = results[0].boxes.id.cpu().numpy().astype(int)
                    
                    for box, obj_id in zip(boxes, ids):
                        # Convert Pixels to Pitch Meters
                        x_pitch = (box[0] / w) * self.pitch_length
                        y_pitch = (box[1] / h) * self.pitch_width
                        
                        match_data.append({
                            'timestamp': round(frame_idx / fps, 2),
                            'player_id': obj_id,
                            'x': round(x_pitch, 2),
                            'y': round(y_pitch, 2)
                        })
                
                # Update UI Progress
                progress = frame_idx / total_frames
                prog_bar.progress(progress)
                status_text.text(f"ASA AI analyzing match... {int(progress*100)}%")
                
            frame_idx += 1
            
        cap.release()
        return pd.DataFrame(match_data)

    def generate_institutional_pdf(self, df, match_name):
        """Builds the 5-page PDF report structure."""
        pdf = ASAReport()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # --- Page 1: Executive Summary ---
        pdf.add_page()
        pdf.chapter_title("Page 1: Executive Summary")
        pdf.add_metric_row("Match Name", match_name)
        pdf.add_metric_row("Analysis Date", str(datetime.date.today()))
        
        field_tilt = (len(df[df['x'] > 70]) / len(df) * 100) if not df.empty else 0
        pdf.add_metric_row("Territorial Dominance (Field Tilt)", f"{round(field_tilt, 1)}%")

        # --- Page 2: Tactical Shape ---
        pdf.add_page()
        pdf.chapter_title("Page 2: Team Tactical Architecture")
        avg_x = df.groupby('player_id')['x'].mean().mean()
        pdf.add_metric_row("Mean Defensive Line Height", f"{round(avg_x, 2)}m")

        # --- Page 3: Athlete Physical Audit ---
        pdf.add_page()
        pdf.chapter_title("Page 3: Athlete Physical Rankings")
        # Sample ranking
        if not df.empty:
            top_players = df.groupby('player_id').size().sort_values(ascending=False).head(5)
            for pid, count in top_players.items():
                pdf.cell(0, 10, f"Player ID {pid}: High Engagement Score ({count} tactical events)", ln=True)

        # --- Page 4 & 5 (Scouting & Recommendations) ---
        pdf.add_page()
        pdf.chapter_title("Page 4: ASA Global Scouting Spotlight")
        pdf.add_page()
        pdf.chapter_title("Page 5: Actionable Coaching Recommendations")

        # Return byte string for Streamlit download
        return pdf.output(dest='S').encode('latin-1')

# --- STREAMLIT UI BOILERPLATE ---
st.set_page_config(page_title="ASA Global | Match Intelligence", layout="wide")

st.sidebar.title("🦁 ASA Global")
st.sidebar.info("2026 Institutional Analysis Suite")

st.title("⚽ Full-Match Tactical Production")

st.subheader("Step 1: Ingest Match Footage")
source_type = st.radio("Select Source", ["Cloud Link (Recommended for 2GB+)", "Local Upload (Small Clips)"])

video_path = None

if source_type == "Local Upload (Small Clips)":
    video_file = st.file_uploader("Upload Clip", type=['mp4', 'mov', 'avi'])
    if video_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            tmp.write(video_file.read())
            video_path = tmp.name
else:
    video_url = st.text_input("Paste Direct Video Link (Google Drive/Dropbox Direct Link)")
    if video_url:
        video_path = video_url # OpenCV can read direct streaming URLs

    if st.button("🚀 EXECUTE FULL ANALYSIS"):
        core = ASAGlobalCore()
        
        with st.status("Initializing ASA Engine...", expanded=True) as status:
            data = core.process_match_stream(video_path)
            status.update(label="Analysis Complete!", state="complete", expanded=False)
            
        if not data.empty:
            st.success("Analysis finalized. System ready for reporting.")
            
            # Show a tactical glimpse
            st.subheader("Tactical Density (Live Sample)")
            st.scatter_chart(data=data.head(500), x='x', y='y', color='player_id')
            
            # PDF Generation
            pdf_bytes = core.generate_institutional_pdf(data, video_file.name)
            
            st.download_button(
                label="📥 DOWNLOAD 5-PAGE INSTITUTIONAL REPORT",
                data=pdf_bytes,
                file_name=f"ASA_Report_{video_file.name}.pdf",
                mime="application/pdf"
            )
            
            # Cleanup temp file
            os.remove(video_path)
        else:
            st.error("No players detected. Please ensure the footage is tactical wide-angle.")
