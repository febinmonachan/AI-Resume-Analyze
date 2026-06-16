import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="centered"
)

# Title
st.title("📄 AI Resume Analyzer")

st.markdown("""
Analyze your resume using AI and receive:

- ATS Score
- Resume Strengths
- Improvement Suggestions
- Keyword Analysis
- Section-wise Feedback
""")

st.divider()

# Input Method
input_method = st.radio(
    "Choose Resume Input Method",
    ["Upload PDF", "Paste Text"]
)

if input_method == "Upload PDF":
    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf"]
    )

else:
    resume_text = st.text_area(
        "Paste Resume Text",
        height=250
    )

st.divider()

analyze_button = st.button(
    "Analyze Resume",
    use_container_width=True
)

if analyze_button:
    st.info("Analysis feature coming in next step...")
