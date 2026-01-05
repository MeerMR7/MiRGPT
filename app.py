import streamlit as st
import pdfplumber
from groq import Groq
import os

# --- 1. PAGE CONFIG & PROFESSIONAL STYLE ---
st.set_page_config(page_title="MiRGPT", page_icon="🛡️", layout="centered")

# Custom CSS for a clean, professional "Executive" look
st.markdown("""
    <style>
    /* Main Title Styling */
    .main-title {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        color: #1E1E1E;
        text-align: center;
        margin-top: -50px;
        letter-spacing: -1px;
    }
    .sub-text {
        text-align: center;
        color: #555;
        font-size: 1.2rem;
        margin-bottom: 40px;
        font-style: italic;
    }
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #F0F2F6;
        border-right: 1px solid #e0e0e0;
    }
    /* Chat Bubble Tweaks */
    .stChatMessage {
        border-radius: 15px;
    }
    </style>
""", unsafe_allow_html=True) # Corrected from unsafe_allow_stdio

# --- 2. CONNECT TO GROQ CLOUD ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ API Key missing! Add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. OPTIMIZED KNOWLEDGE ENGINE ---
PDF_FILE = "Academic-Policy-Manual-for-Students3.pdf"

@st.cache_data
def load_university_manual():
    if not os.path.exists(PDF_FILE):
        return None
    full_text = ""
    with pdfplumber.open(PDF_FILE) as pdf:
        # Load the most relevant pages for speed
        for page in pdf.pages[:30]: 
            content = page.extract_text()
            if content: full_text += content + "\n"
    return full_text

manual_text = load_university_manual()

# --- 4. PROFESSIONAL SIDEBAR ---
with st.sidebar:
    st.markdown("## 🛡️ MiRGPT")
    st.caption("v2.5 • Premium Academic Intelligence")
    st.divider()
    st.markdown("### 📋 Active Policies")
    st.info("""
    - **Grading Criteria** 2025
    - **Attendance Rules** (80%)
    - **GPA/Probation** Limits
    - **Exam Regulations**
    """)
    st.divider()
    if st.button("🔄 Start New Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 5. MAIN INTERFACE ---
st.markdown('<p class="main-title">MiRGPT</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Intelligent University Policy Navigator</p>', unsafe_allow_html=True)

if not manual_text:
    st.error(f"❌ Document `{PDF_FILE}` not found. Please check your GitHub files.")
    st.stop()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalam o Alaikum! I am **MiRGPT**. I have analyzed your university's academic manual. How can I help you today?"}
    ]

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input & High-Speed Streaming
if prompt := st.chat_input("Ask about attendance, GPA, or policies..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_box = st.empty()
        full_response = ""
        
        try:
            # Using the new 2026-supported model: llama-3.1-8b-instant
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"You are MiRGPT, a professional academic advisor. Use ONLY this text to answer: {manual_text[:15000]}. Be formal, precise, and helpful."},
                    {"role": "user", "content": prompt}
                ],
                stream=True, 
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_box.markdown(full_response + "▌")
            
            response_box.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Brain Error: {e}")
