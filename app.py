import streamlit as st
import pdfplumber
from groq import Groq
import os

# --- MiRGPT CLOUD ADVISOR ---
st.set_page_config(page_title="MiRGPT | Academic Advisor", page_icon="🎓")

# 1. Connect to the Groq Brain using your Secret Key
if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing API Key! Please add 'GROQ_API_KEY' to Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. Load the Policy PDF
PDF_PATH = "Academic-Policy-Manual-for-Students3.pdf"

@st.cache_data
def load_policy_text():
    if not os.path.exists(PDF_PATH):
        return "Policy file not found."
    text = ""
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content: text += content + "\n"
    return text

policy_knowledge = load_policy_text()

# --- UI INTERFACE ---
st.title("🎓 MiRGPT Academic Advisor")
st.caption("Powered by Groq Llama 3 • Official Policy Expert")

# Sidebar with info
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3429/3429149.png", width=100)
    st.header("Advisor Toolbox")
    st.info("Core Policies Loaded:\n* 80% Attendance\n* 1.70 Probation\n* Spring 2025 Grading")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Assalam o Alaikum! I have read the University Policy. How can I help you with your grades or attendance today?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask about GPA, attendance, or exams..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Send context to Groq
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": f"You are MiRGPT, a professional Academic Advisor at Iqra University. Answer using this policy: {policy_knowledge[:12000]}"},
                    {"role": "user", "content": prompt}
                ],
            )
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Brain Error: {e}")
