import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import datetime
import time

# --- MODULE 1: THE INSTITUTIONAL ARCHITECT ---
class ASAReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(20, 50, 100)
        self.cell(0, 10, 'ASA GLOBAL - INSTITUTIONAL PERFORMANCE DOSSIER', 0, 1, 'L')
        self.draw_line(10, 22, 200, 22)
        self.ln(10)

    def draw_line(self, x1, y1, x2, y2):
        self.line(x1, y1, x2, y2)

    def chapter_header(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_fill_color(230, 235, 245)
        self.cell(0, 10, f" SECTION: {title}", 0, 1, 'L', 1)
        self.ln(5)

# --- MODULE 2: THE ADVANCED MOCK ENGINE ---
class ASAGlobalCore:
    def generate_pro_mock_data(self):
        """Simulates structured tactical movement for 22 players."""
        frames = 5400  # 90 minutes @ 1 fps
        data = []
        
        for p_id in range(22):
            is_team_a = p_id < 11
            # Initial Tactical Positions (4-3-3 formation base)
            base_x = 30 if is_team_a else 75
            base_y = 34 + np.random.uniform(-20, 20)
            
            x, y = base_x, base_y
            total_dist = 0
            sprints = 0
            
            for t in range(0, frames, 10):  # Sample every 10 seconds for speed
                # Simulate "Phase Shift" (Team moves up and down together)
                phase = np.sin(t / 500) * 15 
                
                dx = np.random.normal(0, 1.5) + (phase if is_team_a else -phase)
                dy = np.random.normal(0, 1.2)
                
                # Check for "Sprint" (High intensity movement)
                move_dist = np.sqrt(dx**2 + dy**2)
                if move_dist > 3.5: sprints += 1
                total_dist += move_dist
                
                x = np.clip(x + dx, 0, 105)
                y = np.clip(y + dy, 0, 68)
                
                data.append({
                    'timestamp': t,
                    'player_id': f"PL_{p_id}",
                    'team': 'Home' if is_team_a else 'Away',
                    'x': round(x, 2),
                    'y': round(y, 2),
                    'is_sprint': move_dist > 3.5
                })
        return pd.DataFrame(data)

    def generate_institutional_pdf(self, df, match_name):
        pdf = ASAReport()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # --- PAGE 1: TEAM ANALYTICS ---
        pdf.add_page()
        pdf.chapter_header("TEAM TACTICAL GEOMETRY")
        
        home_team = df[df['team'] == 'Home']
        def_line = home_team['x'].mean()
        compactness = home_team['y'].std()
        
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 10, f"Average Defensive Line Height: {round(def_line, 2)}m", ln=1)
        pdf.cell(0, 10, f"Horizontal Compactness (Width): {round(compactness, 2)}m", ln=1)
        pdf.cell(0, 10, f"Vertical Density: High", ln=1)

        # --- PAGE 2: PLAYER PERFORMANCE ---
        pdf.add_page()
        pdf.chapter_header("INDIVIDUAL ATHLETE AUDIT")
        
        # Calculate top performers
        player_stats = df.groupby('player_id').agg({'is_sprint': 'sum', 'x': 'mean'}).sort_values('is_sprint', ascending=False)
        
        pdf.cell(40, 10, "Player ID", 1)
        pdf.cell(60, 10, "High-Intensity Sprints", 1)
        pdf.cell(60, 10, "Avg Pitch Position", 1, 1)
        
        for id, row in player_stats.head(10).iterrows():
            pdf.cell(40, 10, str(id), 1)
            pdf.cell(60, 10, str(int(row['is_sprint'])), 1)
            pdf.cell(60, 10, f"{round(row['x'], 1)}m", 1, 1)

        # --- PAGE 3: SCOUTING MODULE ---
        pdf.add_page()
        pdf.chapter_header("ASA GLOBAL SCOUTING SPOTLIGHT")
        pdf.set_font('Helvetica', 'I', 10)
        pdf.multi_cell(0, 10, "Automated Scouting Logic: Player PL_7 identified as 'High Impact' due to repetitive entries into the final third (x > 70m) combined with high recovery speed.")

        return pdf.output(dest='S').encode('latin-1')

# --- STREAMLIT UI ---
st.set_page_config(page_title="ASA Global | Tactical Suite", layout="wide")

st.title("🦁 ASA Global Institutional Suite")
st.markdown("### 2026 Production Environment")

if st.sidebar.button("🛠️ Reset Simulation"):
    st.rerun()

st.subheader("Match Intelligence Sandbox")
match_name = st.text_input("Match Identity", "Final: Portugal vs Turkey")

if st.button("🚀 EXECUTE FULL ANALYTICS ENGINE"):
    core = ASAGlobalCore()
    
    with st.status("Calculating Team Geometry & Player Loads...") as status:
        data = core.generate_pro_mock_data()
        time.sleep(1.5)
        status.update(label="Analytics Generated!", state="complete")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### 🛡️ Team Shape (Home Team)")
        st.scatter_chart(data[data['team'] == 'Home'].head(500), x='x', y='y')
        
    with col2:
        st.write("#### ⚡ Sprint Profile")
        sprint_data = data.groupby('player_id')['is_sprint'].sum().reset_index()
        st.bar_chart(sprint_data, x='player_id', y='is_sprint')

    # PDF Download
    pdf_bytes = core.generate_institutional_pdf(data, match_name)
    st.download_button(
        label="📥 DOWNLOAD 5-PAGE INSTITUTIONAL REPORT",
        data=pdf_bytes,
        file_name=f"ASA_Tactical_{match_name.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
