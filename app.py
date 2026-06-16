import streamlit as st
import anthropic
import json
import pdfplumber
import io

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="centered"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f0f1a; }
    .stApp { background-color: #0f0f1a; color: #e2e8f0; }
    .score-card {
        background: #1e1e3a;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        border: 1px solid #ffffff15;
    }
    .big-score { font-size: 2.5rem; font-weight: 800; }
    .tag {
        display: inline-block;
        background: #6366f120;
        border: 1px solid #6366f140;
        border-radius: 99px;
        padding: 4px 12px;
        font-size: 0.8rem;
        color: #a5b4fc;
        margin: 4px;
    }
</style>
""", unsafe_allow_html=True)


# ── Helper: extract text from PDF ────────────────────────────
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()


# ── Helper: call Claude API ───────────────────────────────────
def analyze_resume(resume_text: str, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = """You are an expert resume analyst and career coach with 15+ years of HR experience.

Analyze the resume and return ONLY a valid JSON object with this structure:
{
  "overall_score": <0-100>,
  "summary": "<2-3 sentence honest assessment>",
  "sections": {
    "impact":          { "score": <0-100>, "feedback": "<text>", "tips": ["<tip1>", "<tip2>"] },
    "skills":          { "score": <0-100>, "feedback": "<text>", "tips": ["<tip1>", "<tip2>"] },
    "experience":      { "score": <0-100>, "feedback": "<text>", "tips": ["<tip1>", "<tip2>"] },
    "education":       { "score": <0-100>, "feedback": "<text>", "tips": ["<tip1>", "<tip2>"] },
    "ats_compatibility":{ "score": <0-100>, "feedback": "<text>", "tips": ["<tip1>", "<tip2>"] }
  },
  "strengths":    ["<s1>", "<s2>", "<s3>"],
  "improvements": ["<i1>", "<i2>", "<i3>"],
  "keywords":     ["<k1>", "<k2>", "<k3>", "<k4>", "<k5>"]
}

Return ONLY the JSON. No markdown, no explanation."""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Analyze this resume:\n\n{resume_text}"}]
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


# ── Helper: score color ───────────────────────────────────────
def score_color(score):
    if score >= 75:
        return "🟢"
    elif score >= 50:
        return "🟡"
    else:
        return "🔴"


# ══════════════════════════════════════════════════════════════
#  UI STARTS HERE
# ══════════════════════════════════════════════════════════════

st.title("📄 AI Resume Analyzer")
st.markdown("*Get instant AI feedback on your resume — score, strengths, and actionable tips.*")
st.divider()

# ── Sidebar: API Key ─────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your free key at console.anthropic.com"
    )
    st.markdown("👉 [Get free API key](https://console.anthropic.com)")
    st.divider()
    st.caption("Your resume data is never stored.")

# ── Input: PDF or Text ───────────────────────────────────────
input_method = st.radio("How do you want to input your resume?",
                        ["📎 Upload PDF", "📝 Paste Text"],
                        horizontal=True)

resume_text = ""

if input_method == "📎 Upload PDF":
    uploaded = st.file_uploader("Upload your resume PDF", type=["pdf"])
    if uploaded:
        with st.spinner("Extracting text from PDF..."):
            resume_text = extract_text_from_pdf(uploaded)
        st.success(f"✅ Extracted {len(resume_text)} characters from PDF")
        with st.expander("Preview extracted text"):
            st.text(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)
else:
    resume_text = st.text_area(
        "Paste your resume text here",
        height=300,
        placeholder="Copy and paste your full resume here..."
    )

# ── Analyze Button ────────────────────────────────────────────
st.divider()
analyze_btn = st.button("✨ Analyze My Resume", type="primary", use_container_width=True)

if analyze_btn:
    if not api_key:
        st.error("⚠️ Please enter your Anthropic API key in the sidebar.")
    elif not resume_text.strip():
        st.error("⚠️ Please upload a PDF or paste your resume text.")
    else:
        with st.spinner("🤖 Claude is analyzing your resume..."):
            try:
                result = analyze_resume(resume_text, api_key)

                # ── Overall Score ─────────────────────────────
                st.divider()
                st.subheader("📊 Overall Score")

                col1, col2 = st.columns([1, 2])
                with col1:
                    score = result["overall_score"]
                    color = "green" if score >= 75 else "orange" if score >= 50 else "red"
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="big-score" style="color:{color}">{score}</div>
                        <div style="color:#64748b; font-size:0.85rem">out of 100</div>
                        <div style="margin-top:8px">{score_color(score)} {'Strong' if score >= 75 else 'Average' if score >= 50 else 'Needs Work'}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"**Summary:** {result['summary']}")

                # ── Section Scores ────────────────────────────
                st.divider()
                st.subheader("📈 Section Breakdown")

                section_labels = {
                    "impact": "🎯 Impact & Achievements",
                    "skills": "⚡ Skills",
                    "experience": "💼 Experience",
                    "education": "🎓 Education",
                    "ats_compatibility": "🤖 ATS Compatibility"
                }

                for key, label in section_labels.items():
                    sec = result["sections"][key]
                    with st.expander(f"{label}  —  {score_color(sec['score'])} **{sec['score']}/100**"):
                        st.progress(sec["score"] / 100)
                        st.markdown(f"**Feedback:** {sec['feedback']}")
                        st.markdown("**Tips:**")
                        for tip in sec["tips"]:
                            st.markdown(f"- 💡 {tip}")

                # ── Strengths & Improvements ──────────────────
                st.divider()
                col3, col4 = st.columns(2)

                with col3:
                    st.subheader("✅ Strengths")
                    for s in result["strengths"]:
                        st.success(s)

                with col4:
                    st.subheader("⚠️ Improvements")
                    for i in result["improvements"]:
                        st.warning(i)

                # ── Keywords ──────────────────────────────────
                st.divider()
                st.subheader("🔑 Detected Keywords")
                tags_html = "".join([f'<span class="tag">{kw}</span>' for kw in result["keywords"]])
                st.markdown(tags_html, unsafe_allow_html=True)

                st.divider()
                st.success("✅ Analysis complete! Fix the improvements above and re-analyze to improve your score.")

            except json.JSONDecodeError:
                st.error("❌ Failed to parse AI response. Please try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
