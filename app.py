import streamlit as st
import pdfplumber
import requests
import datetime
import os

# -------------------- MiRGPT ADVISOR SETUP --------------------
st.set_page_config(
    page_title="MiRGPT | Academic Policy Advisor", 
    page_icon="🎓", 
    layout="centered"
)

# Constants
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3" 
# Use the specific file path you requested
PDF_PATH = "data/Academic-Policy-Manual-for-Students3.pdf"

# -------------------- SECURE DATA LOADING --------------------
@st.cache_data
def load_advisor_knowledge(max_chars: int = 1000):
    if not os.path.exists(PDF_PATH):
        return []
    
    all_text = ""
    try:
        with pdfplumber.open(PDF_PATH) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"
    except Exception as e:
        st.error(f"Advisor Error: Could not read policy file. {e}")
        return []

    # Chunking for high-accuracy retrieval
    raw_lines = [line.strip() for line in all_text.split("\n") if line.strip()]
    chunks, current_chunk = [], ""
    for line in raw_lines:
        if len(current_chunk) + len(line) <= max_chars:
            current_chunk += " " + line
        else:
            chunks.append(current_chunk.strip())
            current_chunk = line
    if current_chunk: chunks.append(current_chunk.strip())
    return chunks

policy_data = load_advisor_knowledge()

# -------------------- ADVISOR LOGIC --------------------
def find_policy_context(query, top_k=3):
    if not policy_data: return ""
    query_tokens = set(query.lower().split())
    matches = []
    for chunk in policy_data:
        score = len(query_tokens & set(chunk.lower().split()))
        if score > 0: matches.append((score, chunk))
    matches.sort(reverse=True, key=lambda x: x[0])
    return "\n\n".join([m[1] for m in matches[:top_k]])

def ask_ollama(messages):
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME, "messages": messages, "stream": False
        })
        return response.json()["message"]["content"]
    except:
        return "⚠️ Advisor Offline: Please ensure Ollama is running Llama 3."

# -------------------- PROFESSIONAL UI --------------------
st.title("🎓 MiRGPT Academic Advisor")
st.markdown("---")

# Quick Reference Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3429/3429149.png", width=100)
    st.header("Advisor Toolbox")
    st.info("""
    **Core Policies Loaded:**
    - 80% Attendance Requirement
    - 1.70 Probation Threshold
    - Spring 2025 Grading Scheme
    - Course Withdrawal (W) Rules
    """)
    if st.button("Clear Consultation"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "Assalam o Alaikum! I am your **MiRGPT Academic Advisor**. How can I help you with your grades, attendance, or university policies today?"
    }]

# Display Conversation
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Student Input
if user_query := st.chat_input("Ask about probation, attendance, GPA..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        context = find_policy_context(user_query)
        today = datetime.datetime.now().strftime("%B %d, %Y")
        
        # Specialist System Prompt
        system_prompt = f"""
        You are the 'MiRGPT Academic Policy Advisor' for Iqra University. 
        Your goal is to provide accurate, authoritative advice based on the provided PDF context.
        
        CRITICAL KNOWLEDGE:
        - Attendance: 80% is mandatory. Below 80% = XF Grade.
        - Probation: Below 1.70 Semester GPA (Undergrad).
        - Passing: 50/100 marks for Undergrad.
        
        If the question is about rules, strictly use the Context: {context}
        Current Date: {today}. 
        Language: Roman Urdu or English. Be professional and supportive.
        """
        
        history = [{"role": "system", "content": system_prompt}]
        history.extend(st.session_state.messages[-4:])
        
        with st.spinner("Reviewing University Policy..."):
            answer = ask_ollama(history)
            st.markdown(answer)
            if context:
                with st.expander("Reference from Policy Manual"):
                    st.caption(context)

    st.session_state.messages.append({"role": "assistant", "content": answer})
