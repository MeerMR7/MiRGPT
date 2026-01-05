import streamlit as st
import pdfplumber
from groq import Groq
import os

# --- 1. SETTINGS & PAGE CONFIG ---
st.set_page_config(page_title="MiRGPT | Academic Advisor", page_icon="🎓", layout="centered")

# --- 2. CONNECT TO THE BRAIN (GROQ) ---
# This looks for the key you saved in the "Secrets" box
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ API Key not found! Go to Settings > Secrets and add your GROQ_API_KEY.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. LOAD THE UNIVERSITY POLICY PDF ---
# Make sure this name matches your file on GitHub EXACTLY
PDF_NAME = "Academic-Policy-Manual-for-Students3.pdf"

@st.cache_data
def load_policy_text(filename):
    if not os.path.exists(filename):
        return None
    extracted_text = ""
    try:
        with pdfplumber.open(filename) as pdf:
            for page in pdf.pages:
                page_content = page.extract_text()
                if page_content:
                    extracted_text += page_content + "\n"
        return extracted_text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

# Extract the text from your manual
policy_knowledge = load_policy_text(PDF_NAME)

# --- 4. THE CHAT INTERFACE ---
st.title("🎓 MiRGPT: Academic Advisor")
st.markdown(f"**Currently Reading:** `{PDF_NAME}`")
st.divider()

if not policy_knowledge:
    st.warning(f"❌ Could not find `{PDF_NAME}`. Please upload it to your GitHub repository.")
    st.stop()

# Initialize memory (Chat History)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalam o Alaikum! I am MiRGPT. I have read the policy manual. How can I help you today?"}
    ]

# Show previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about attendance, GPA, or grading..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from AI
    with st.chat_message("assistant"):
        try:
            # We use 'llama-3.1-8b-instant' because 'llama3-8b-8192' is outdated in 2026.
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"You are MiRGPT, a professional university advisor. Use ONLY this text to answer: {policy_knowledge[:15000]}"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2, # Keeps answers accurate and professional
            )
            ai_response = completion.choices[0].message.content
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            st.error(f"Brain Error: {e}")
