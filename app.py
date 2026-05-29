import streamlit as st
from frontend.main_app import render_upload_section, render_results_section
from frontend.chat_interface import render_chat_interface

# Set the page layout to wide for better visual presentation
st.set_page_config(page_title="ATS Resume Checker", layout="wide", initial_sidebar_state="collapsed")

def load_css():
    st.markdown("""
        <style>
        /* Base Dark Theme */
        .stApp {
            background-color: #0e1117;
            color: #c9d1d9;
        }
        
        /* Hide sidebar completely if not used */
        [data-testid="collapsedControl"] { display: none; }
        
        /* Style the main title */
        h1, h2, h3 {
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
        }
        
        /* File Uploader Customization: Hide default SVG icon (remove symbols for files) */
        [data-testid="stFileUploadDropzone"] svg {
            display: none;
        }
        
        /* Button styling */
        .stButton>button {
            width: 100%;
            background-color: #5865F2; /* A nice purple/blue for primary actions */
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 12px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #4752C4;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(88, 101, 242, 0.4);
        }
        
        /* Information Cards */
        .info-card {
            background-color: #161b22;
            padding: 24px;
            border-radius: 12px;
            border: 1px solid #30363d;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            margin-bottom: 24px;
        }
        .info-card h3 {
            margin-top: 0;
            font-size: 18px;
            color: #ffffff;
        }
        .info-card ul {
            color: #8b949e;
            line-height: 1.8;
            margin-bottom: 0;
        }
        .info-card p {
            color: #8b949e;
            margin-bottom: 0;
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    load_css()
    
    st.title("ATS Resume Checker")
    st.markdown("<p style='color: #8b949e; font-size: 16px;'>Upload your resume with drag and drop, compare it against a job description, and get a polished ATS-style analysis with scores, risks, keywords, and actionable rewrites.</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #30363d;'>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2], gap="large")

    with col1:
        render_upload_section()

    with col2:
        if "analysis" in st.session_state:
            render_results_section()
            st.markdown("<hr style='border-color: #30363d;'>", unsafe_allow_html=True)
            render_chat_interface()
        else:
            st.markdown("""
                <div class="info-card">
                    <h3>What You'll Get</h3>
                    <ul>
                        <li>Overall ATS-style score and grade</li>
                        <li>Section-by-section scoring breakdown</li>
                        <li>ATS risks and why they matter</li>
                        <li>Missing keyword suggestions</li>
                        <li>Ready-to-use rewrite recommendations</li>
                        <li>Interactive AI Chat to discuss your resume</li>
                    </ul>
                </div>
                <div class="info-card">
                    <h3>Privacy</h3>
                    <p>Uploaded files are sent for parsing and analysis, and the temporary uploaded file is deleted server-side after extraction.</p>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
