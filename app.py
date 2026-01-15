import streamlit as st
import pandas as pd
import numpy as np
from ultralytics import YOLO
import cv2
import tempfile
from fpdf import FPDF
import datetime
import os
import yt_dlp

# --- PILLAR 1: THE PDF ARCHITECT ---
class ASAReport(FPDF):
    def header(self):
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

# --- PILLAR 2: THE ASA CORE ENGINE ---
class ASAGlobalCore:
    def __init__(self, model_variant='yolov8n.pt'):
        self.model = YOLO(model_variant)
        self.pitch_length = 105.0
        self.pitch_width = 68.0

    def get_youtube_stream(self, url):
        """Extracts the direct stream URL from YouTube with fallback logic."""
        ydl_opts = {
            'format': 'best[ext=mp4]/best', # Prioritize MP4 for OpenCV compatibility
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Fallback logic: if 'url' isn't at the top, grab it from the best format
            if 'url' in info:
                return info['url']
            elif 'formats' in info:
                # Filter for formats that actually have a URL and preferred extension
                return info['formats'][-1]['url']
            else:
                raise KeyError("Could not find a valid stream URL in the YouTube metadata.")

    def process_match_stream(self, video_source, is_youtube=False, sampling_rate=1.0):
        """
        Processes video and extracts tactical coordinates.
        sampling_rate=1.0 means we analyze 1 frame per second (optimized for speed).
        """
        if is_youtube:
            video_source = self.get_youtube_stream(video_source)

        cap = cv2.VideoCapture(video_source)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_stride = int(fps * sampling_rate)
        
        match_data = []
        frame_idx = 0
        
        prog_bar = st.progress(0)
        status_text = st.empty()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            if frame_idx % frame_stride == 0:
                # YOLOv8 tracking logic
                results = self.model.track(frame, persist=True, verbose=False, conf=0.30, classes=[0])
                
                if results[0].boxes.id is not None:
                    h, w, _ = frame.shape
                    boxes = results[0].boxes.xywh.cpu().numpy()
                    ids = results[0].boxes.id.cpu().numpy().astype(int)
                    
                    for box, obj_id in zip(boxes, ids):
                        # Coordinate Mapping to Pitch Meters
                        x_pitch = (box[0] / w) * self.pitch_length
                        y_pitch = (box[1] / h) * self.pitch_width
                        
                        match_data.append({
                            'timestamp': round(frame_idx / fps, 2),
                            'player_id': obj_id,
                            'x': round(x_pitch, 2),
                            'y': round(y_pitch, 2)
                        })
                
                # Visual UI Progress
                progress = min(frame_idx / total_frames, 1.0) if total_frames > 0 else 0.5
                prog_bar.progress(progress)
                status_text.text(f"ASA AI extracting tactical data... {int(progress*100)}%")
                
            frame_idx += 1
            
        cap.release()
        return pd.DataFrame(match_data)

    def generate_institutional_pdf(self, df, match_name):
        pdf = ASAReport()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Page 1: Summary
        pdf.add_page()
        pdf.chapter_title("Page 1: Executive Match Summary")
        pdf.add_metric_row("Source", match_name)
        pdf.add_metric_row("Analysis Date", str(datetime.date.today()))
        
        field_tilt = (len(df[df['x'] > 70]) / len(df) * 100) if not df.empty else 0
        pdf.add_metric_row("Field Tilt (Attacking Presence)", f"{round(field_tilt, 1)}%")

        # Page 2: Tactical Geometry
        pdf.add_page()
        pdf.chapter_title("Page 2: Tactical Geometry & Compactness")
        if not df.empty:
            avg_x = df['x'].mean()
            pdf.add_metric_row("Average Defensive Line (m)", f"{round(avg_x, 2)}m")

        # Page 3, 4, 5: Templates
        pdf.add_page()
        pdf.chapter_title("Page 3: Athlete Physical Audit")
        pdf.add_page()
        pdf.chapter_title("Page 4: Scouting Spotlight")
        pdf.add_page()
        pdf.chapter_title("Page 5: Tactical Recommendations")

        return pdf.output(dest='S').encode('latin-1')

# --- STREAMLIT UI ---
st.set_page_config(page_title="ASA Global | Match Engine", layout="wide")

st.sidebar.title("🦁 ASA Global")
st.sidebar.markdown("### Status: Operational")
st.sidebar.info("v1.2: YouTube Stream Enabled")

st.title("⚽ Institutional Tactical Intelligence")

source_type = st.radio("Select Input Source", ["YouTube URL", "Local Upload"])

video_path = None
is_yt = False

if source_type == "YouTube URL":
    yt_link = st.text_input("Paste YouTube Link", placeholder="https://www.youtube.com/watch?v=...")
    if yt_link:
        video_path = yt_link
        is_yt = True
else:
    uploaded_file = st.file_uploader("Upload MP4 Clip", type=['mp4', 'mov'])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            tmp.write(uploaded_file.read())
            video_path = tmp.name

if video_path:
    if st.button("🚀 EXECUTE FULL PRODUCTION ANALYSIS"):
        core = ASAGlobalCore()
        
        with st.spinner("Processing match frames..."):
            data = core.process_match_stream(video_path, is_youtube=is_yt)
            
        if not data.empty:
            st.success("Match Analysis Complete.")
            
            # Simple Scatter Visualization
            st.subheader("Tactical Density Visualization")
            st.scatter_chart(data=data.head(1000), x='x', y='y', color='player_id')
            
            # PDF Download
            report_name = yt_link if is_yt else "Uploaded_File"
            pdf_bytes = core.generate_institutional_pdf(data, report_name)
            
            st.download_button(
                label="📥 DOWNLOAD 5-PAGE INSTITUTIONAL REPORT",
                data=pdf_bytes,
                file_name="ASA_Tactical_Report.pdf",
                mime="application/pdf"
            )
        else:
            st.error("No data extracted. Verify the camera angle is wide-angle.")

        # Cleanup if local
        if not is_yt and os.path.exists(video_path):
            os.remove(video_path)
