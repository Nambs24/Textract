import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import streamlit as st
from pathlib import Path
from services.agent_runner import AgentSession

st.set_page_config(page_title="Textract AI", layout="wide")
st.title("🤖 Textract — AI Professional Intelligence Agent")

# ---------------- GLOBAL SESSION STATE ----------------

if "profiles" not in st.session_state:
    st.session_state.profiles = {}

if "active_profile" not in st.session_state:
    st.session_state.active_profile = None

# ---------------- SIDEBAR ----------------

st.sidebar.header("👤 Profiles")

new_profile = st.sidebar.text_input("Create / Switch Profile")

if st.sidebar.button("Activate Profile"):

    if new_profile:

        if new_profile not in st.session_state.profiles:
            st.session_state.profiles[new_profile] = AgentSession()

        st.session_state.active_profile = new_profile

# ---------------- ACTIVE PROFILE ----------------

profile = st.session_state.active_profile

if profile:
    agent = st.session_state.profiles[profile]
    st.sidebar.success(f"Active: {profile}")
else:
    st.warning("Create or select a profile to begin")
    st.stop()

# ---------------- INGEST SECTION ----------------

st.sidebar.divider()
st.sidebar.header("📂 Data Preload")

github_username = st.sidebar.text_input("GitHub Username")

if st.sidebar.button("Ingest GitHub Data"):

    with st.spinner("Fetching GitHub data..."):
        agent.ingest_github(github_username)

    st.sidebar.success("GitHub Data Saved✅")

resume_file = st.sidebar.file_uploader(
    "Upload Resume",
    type=["pdf", "docx", "txt"]
)

if st.sidebar.button("Ingest Resume") and resume_file:

    temp_path = Path("temp_uploaded_resume") / resume_file.name
    temp_path.parent.mkdir(exist_ok=True)

    with open(temp_path, "wb") as f:
        f.write(resume_file.read())

    with st.spinner("Processing resume..."):
        agent.ingest_resume(str(temp_path), profile)

    st.sidebar.success("Resume ingested ✅")

# ---------------- RESET ----------------

if st.sidebar.button("🔄 Reset Profile Memory"):
    agent.reset()
    st.sidebar.success("Memory cleared")

# ---------------- CHAT HISTORY ----------------

for msg in agent.state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- CHAT INPUT ----------------

user_input = st.chat_input("Ask about this profile...")

if user_input:

    agent.state.chat_history.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = agent.ask(user_input)

        st.markdown(response)