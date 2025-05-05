import streamlit as st
from openai import OpenAI

# ————— CONFIGURATION —————
MODEL_NAME = "gpt-4.1"
# Paste or load your complete resume/instructions here:
RESUME_CONTENT = """
<Your complete system-level resume and instructions go here.>
"""

# ————— APP START —————
st.set_page_config(page_title="🔐 Invisible-Prompt Chatbot", layout="wide")

st.title("💬 Invisible-Prompt Chatbot")

# —– Sidebar: select your role
role = st.sidebar.radio("Who are you?", ("Operator", "Viewer"))

# —– API Key Entry
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
st.session_state.api_key = st.sidebar.text_input(
    "OpenAI API Key", type="password", value=st.session_state.api_key
)
if not st.session_state.api_key:
    st.warning("Enter your OpenAI API key to continue.")
    st.stop()

client = OpenAI(api_key=st.session_state.api_key)

# —– Initialize conversation storage
if "conversations" not in st.session_state:
    # Each entry: {"user": str, "assistant": str}
    st.session_state.conversations = []

# —– Operator UI: full history + new prompt
if role == "Operator":
    # Show full history
    if st.session_state.conversations:
        st.markdown("### Full Conversation")
        for i, turn in enumerate(st.session_state.conversations, start=1):
            st.markdown(f"**You #{i}:** {turn['user']}")
            st.markdown(f"**Bot #{i}:** {turn['assistant']}")
            st.write("---")

    # New input
    prompt = st.chat_input("Your message…")
    if prompt:
        # Call OpenAI
        messages = [
            {"role": "system", "content": RESUME_CONTENT}
        ] + [
            {"role": "user", "content": turn["user"]}
            if idx % 2 == 0 else {"role": "assistant", "content": turn["assistant"]}
            for idx, turn in enumerate(
                sum(([{"user": t["user"]}, {"assistant": t["assistant"]}] 
                     for t in st.session_state.conversations), []), 
                start=0
            )
        ] + [{"role": "user", "content": prompt}]

        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            stream=True,
        )

        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.conversations.append({
            "user": prompt,
            "assistant": response
        })
        st.rerun()

# —– Viewer UI: only selected exchange
else:
    st.markdown("### Select an exchange to view")
    if not st.session_state.conversations:
        st.info("No exchanges have happened yet.")
        st.stop()

    options = [f"Exchange #{i+1}" for i in range(len(st.session_state.conversations))]
    choice = st.selectbox("Which one?", options)
    idx = options.index(choice)
    turn = st.session_state.conversations[idx]

    ## st.markdown(f"**You:** {turn['user']}")
    st.markdown(f"**Bot:** {turn['assistant']}")
