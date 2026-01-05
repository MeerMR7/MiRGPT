import streamlit as st
import pdfplumber
from groq import Groq
import os

st.set_page_config(page_title="MiRGPT | Academic Advisor", page_icon="🎓")

# 1. Connect to Groq
if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing API Key in Secrets!")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. Optimized PDF Extraction (Cached)
@st.cache_data
def get_pdf_knowledge():
    PDF_PATH = "Academic-Policy-Manual-for-Students3.pdf"
    if not os.path.exists(PDF_PATH):
        return "Manual not found."
    
    with st.spinner("Reading University Manual..."):
        text = ""
        with pdfplumber.open(PDF_PATH) as pdf:
            # We only take the most important text to keep it fast
            for page in pdf.pages[:20]: # Limits to first 20 pages for speed
                content = page.extract_text()
                if content: text += content + "\n"
        return text

knowledge_base = get_pdf_knowledge()

# --- CHAT UI ---
st.title("🎓 MiRGPT Advisor")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("How can I help you?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. STREAMING RESPONSE (This makes it feel 10x faster)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # We use stream=True here
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"You are MiRGPT. Answer using this: {knowledge_base[:10000]}"},
                {"role": "user", "content": prompt}
            ],
            stream=True, 
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
                message_placeholder.markdown(full_response + "▌") # Animated cursor
        
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
