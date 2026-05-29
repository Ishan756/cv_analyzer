import streamlit as st
from backend.pdf_ingestion import load_split_pdf
from backend.vector_store import create_vector_store
from backend.analysis import analyze_resume, optimize_resume
import os
import shutil
import re
import html

def render_upload_section():
    st.markdown("""
        <div style="background-color: #161b22; padding: 24px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 16px;">
            <h3 style="margin-top:0; color: #ffffff; font-size: 18px;">Upload Resume</h3>
            <p style="color: #8b949e; font-size: 14px; margin-bottom: 0;">Drag & drop your resume below</p>
        </div>
    """, unsafe_allow_html=True)
    
    resume_file = st.file_uploader("Upload Resume", type=["pdf"], label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background-color: #161b22; padding: 24px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 16px;">
            <h3 style="margin-top:0; color: #ffffff; font-size: 18px;">Job Description</h3>
            <p style="color: #8b949e; font-size: 14px; margin-bottom: 0;">Paste the job description to compare against your resume</p>
        </div>
    """, unsafe_allow_html=True)
    
    job_description = st.text_area("Job Description", height=200, label_visibility="collapsed", placeholder="Paste job description here...")
    
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Smart ATS Analysis", type="primary"):
        if resume_file and job_description:
            with st.spinner("Analyzing your resume..."):
                temp_dir = "temp"
                os.makedirs(temp_dir, exist_ok=True)
                
                resume_file_path = os.path.join(temp_dir, resume_file.name)
                with open(resume_file_path, "wb") as f:
                    f.write(resume_file.getbuffer())
                
                try:
                    resume_docs, resume_chunks = load_split_pdf(resume_file_path)
                    st.session_state.vector_store = create_vector_store(resume_chunks)

                    full_resume = " ".join([doc.page_content for doc in resume_docs])
                    # Save the full resume text for previewing
                    st.session_state.full_resume = full_resume

                    analysis = analyze_resume(full_resume, job_description)
                    # persist job description for later optimization
                    st.session_state.job_description = job_description
                    st.session_state.analysis = analysis
                    # Try to parse matched and unmatched skills from the analysis text
                    matched, unmatched = parse_skills_from_analysis(analysis)
                    st.session_state.matched_skills = matched
                    st.session_state.unmatched_skills = unmatched
                except Exception as e:
                    st.error(f"Error processing file: {e}")
                finally:
                    shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            st.warning("Please provide both a resume and a job description.")

def render_results_section():
    st.markdown("""
        <div style="background-color: #161b22; padding: 24px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 16px;">
            <h3 style="margin-top:0; color: #ffffff; font-size: 18px;">Analysis Results</h3>
        </div>
    """, unsafe_allow_html=True)
    analysis_text = st.session_state.get("analysis", "")

    # Layout: left = resume preview, right = analysis + suggestions
    left, right = st.columns([1, 1])

    with left:
        st.subheader("Resume Preview")
        resume_text = st.session_state.get("full_resume", "")
        if resume_text:
            matched = st.session_state.get("matched_skills", []) or []
            # Highlight matched skills in green
            highlighted = highlight_resume_text(resume_text, matched)
            st.markdown(f"<div style='background-color:#0b0f14; padding:16px; border-radius:8px; color:#c9d1d9;'>{highlighted}</div>", unsafe_allow_html=True)
        else:
            st.info("Full resume preview not available.")

    with right:
        st.subheader("AI Analysis & Suggestions")
        if analysis_text:
            st.markdown("<div style='background-color:#0b0f14; padding:12px; border-radius:8px; color:#c9d1d9;'>" + analysis_text.replace("\n", "<br />") + "</div>", unsafe_allow_html=True)

        matched = st.session_state.get("matched_skills", []) or []
        unmatched = st.session_state.get("unmatched_skills", []) or []

        st.markdown("<hr style='border-color: #30363d;'>", unsafe_allow_html=True)
        st.markdown("**Suggested Adds**")
        for s in unmatched:
            st.markdown(f"<div style='color:#ff6b6b'>● {html.escape(s)}</div>", unsafe_allow_html=True)

        st.markdown("<br>")
        st.markdown("**Detected Matches**")
        for s in matched:
            st.markdown(f"<div style='color:#6be56b'>● {html.escape(s)}</div>", unsafe_allow_html=True)

        st.markdown("<br>")
        # Optimize resume action
        if st.button("Optimize Resume"):
            if not st.session_state.get("full_resume") or not st.session_state.get("job_description"):
                st.error("Resume or job description missing. Re-run analysis first.")
            else:
                with st.spinner("Optimizing resume..."):
                    opt = optimize_resume(st.session_state.full_resume, st.session_state.job_description)
                    # Save structured results
                    st.session_state.optimized_resume = opt.get("optimized_resume")
                    st.session_state.suggested_adds = opt.get("suggested_adds", [])
                    st.session_state.suggested_removals = opt.get("suggested_removals", [])
                    # Update matched/unmatched if provided
                    st.session_state.matched_skills = opt.get("matched_skills", st.session_state.get("matched_skills", []))
                    st.session_state.unmatched_skills = opt.get("unmatched_skills", st.session_state.get("unmatched_skills", []))
                    st.experimental_rerun()

        # Show optimized resume if available
        if st.session_state.get("optimized_resume"):
            st.markdown("<hr style='border-color: #30363d;'>", unsafe_allow_html=True)
            st.subheader("Optimized Resume")
            opt_text = st.session_state.get("optimized_resume", "")
            st.markdown(f"<div style='background-color:#071019; padding:12px; border-radius:8px; color:#c9d1d9;'>{opt_text.replace('\n','<br/>')}</div>", unsafe_allow_html=True)
            # Show suggested removals in red
            removals = st.session_state.get("suggested_removals", []) or []
            if removals:
                st.markdown("**Suggested Removals**")
                for r in removals:
                    st.markdown(f"<div style='color:#ff6b6b'>- {html.escape(r)}</div>", unsafe_allow_html=True)

            # Download optimized resume
            if st.button("Download Optimized Resume"):
                st.download_button("Download", opt_text, file_name="optimized_resume.txt")

        st.markdown("**Project Actions**")
        if st.button("Download Suggestions as TXT"):
            suggestions = "Suggested Adds:\n" + "\n".join(unmatched) + "\n\nMatched:\n" + "\n".join(matched)
            st.download_button("Download", suggestions, file_name="resume_suggestions.txt")

        # Allow manual suggestion additions
        new_sugg = st.text_input("Add custom suggestion")
        if st.button("Add Suggestion") and new_sugg:
            st.session_state.unmatched_skills = st.session_state.get("unmatched_skills", []) + [new_sugg]
            st.experimental_rerun()


def parse_skills_from_analysis(analysis_text: str):
    """Try to extract 'Matched Skills' and 'Unmatched Skills' lists from the analysis text."""
    matched = []
    unmatched = []

    if not analysis_text:
        return matched, unmatched

    # Look for headings like 'Matched Skills' and 'Unmatched Skills' and capture list items
    m = re.search(r"Matched Skills[:\s]*\n([\s\S]*?)(?:\n\n|\Z)", analysis_text, re.IGNORECASE)
    if m:
        matched = [line.strip(" -•\t") for line in m.group(1).splitlines() if line.strip()]

    u = re.search(r"Unmatched Skills[:\s]*\n([\s\S]*?)(?:\n\n|\Z)", analysis_text, re.IGNORECASE)
    if u:
        unmatched = [line.strip(" -•\t") for line in u.group(1).splitlines() if line.strip()]

    # Fallback: try to find lines prefixed with 'Matched Skills' inline
    if not matched:
        inline = re.search(r"Matched Skills\s*[:\-]\s*([^\n]+)", analysis_text, re.IGNORECASE)
        if inline:
            matched = [s.strip() for s in re.split(r"[,;]", inline.group(1)) if s.strip()]

    if not unmatched:
        inline2 = re.search(r"Unmatched Skills\s*[:\-]\s*([^\n]+)", analysis_text, re.IGNORECASE)
        if inline2:
            unmatched = [s.strip() for s in re.split(r"[,;]", inline2.group(1)) if s.strip()]

    return matched, unmatched


def highlight_resume_text(text: str, matched_skills: list):
    """Return HTML with matched skill terms highlighted in green."""
    safe = html.escape(text)
    # Limit matches to avoid exploding the HTML
    for skill in sorted(set(matched_skills), key=lambda s: -len(s)):
        if not skill:
            continue
        try:
            pattern = re.compile(r"\b" + re.escape(skill) + r"\b", flags=re.IGNORECASE)
            safe = pattern.sub(lambda m: f"<span style='background:#153f2b; color:#b7f5c3; padding:2px 4px; border-radius:4px;'>{m.group(0)}</span>", safe)
        except re.error:
            continue
    # Replace newlines with <br>
    safe = safe.replace("\n", "<br />")
    return safe
