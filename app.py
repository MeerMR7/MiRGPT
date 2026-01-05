import streamlit as st
import pdfplumber
from groq import Groq
import os

# --- 1. PAGE CONFIG & PROFESSIONAL THEME ---
st.set_page_config(
    page_title="MiRGPT", 
    page_icon="🛡️", 
    layout="centered"
)

# Professional Styling: Subtle and clean
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        color: #1E1E1E;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_allow_stdio=True)

# --- 2. CONNECT TO THE BRAIN ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("API Key missing!")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. SPEED-OPTIMIZED PDF LOADING ---
@st.cache_data
def get_knowledge():
    PDF_PATH = "Academic-Policy-Manual-for-Students3.pdf"
    if not os.path.exists(PDF_PATH):
        return None
    text = ""
    with pdfplumber.open(PDF_PATH) as pdf:
        # Take first 25 pages for maximum speed and accuracy
        for page in pdf.pages[:25]:
            content = page.extract_text()
            if content: text += content + "\n"
    return text

policy_content = get_knowledge()

# --- 4. PROFESSIONAL SIDEBAR ---
with st.sidebar:
    st.markdown("# 🛡️ MiRGPT")
    st.caption("v2.0 • Intelligent Policy Expert")
    st.divider()
    
    st.markdown("### 📋 Core Policies Loaded")
    st.info("""
    - **80% Attendance** Rule
    - **1.70 CGPA** Probation
    - **Spring 2025** Grading
    - **Course Withdrawal** (W)
    """)
    
    st.divider()
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 5. MAIN INTERFACE ---
st.markdown('<p class="main-title">MiRGPT</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Official Academic Policy Knowledge Engine</p>', unsafe_allow_html=True)

if not policy_content:
    st.error(f"⚠️ Policy file not found in repository.")
    st.stop()

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalam o Alaikum! I am **MiRGPT**. I have analyzed the university policy manual. How can I assist you today?"}
    ]

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input & Streaming Logic
if prompt := st.chat_input("Query the policy manual..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # High-speed streaming response
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"You are MiRGPT, a professional academic expert. Use ONLY this manual text: {policy_content[:12000]}. Be concise and polite."},
                    {"role": "user", "content": prompt}
                ],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Connection Error: {e}")
