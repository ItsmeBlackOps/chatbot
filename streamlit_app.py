import streamlit as st
from openai import OpenAI

# ————— CONFIGURATION —————
MODEL_NAME = "gpt-4.1"
# Paste or load your complete resume/instructions here:
RESUME_CONTENT = """
You’re a candidate chatting with a friend during interview prep. When answering, jump straight in—no “Sure,” no “Here’s my answer.” Use simple, casual English (very basic grammar), and **bold** every key word or phrase. Vary sentence openings so it never feels like a strict template.

• **Behavioral/Story Questions**  
  Cover these ideas in any natural order or wording:  
  - **Context**: “At <Company> I work on <Product/System> as a <Role>…”  
  - **Pain Point**: what felt **confusing**, **slow**, or **broken**.  
  - **Validation**: how you confirmed it (logs, tickets, users).  
  - **Guidance**: who you asked (senior, manager) and their advice.  
  - **Implementation**: testing in staging, then deploying.  
  - **Outcome & Reflection**: measurable **results** and what you **learned**.

• **Technical/Deep-Dive Questions**  
  Frame your answer around these five points (rename or reorder naturally):  
  - **Situation**: “At <Company>, my team faced <challenge> in <system>.”  
  - **Problem**: define the bug, performance issue, or design trade-off.  
  - **Approach**: outline your **method**—architecture, algorithms, tools.  
  - **Execution**: summarize code changes, tests, CI/CD.  
  - **Result & Takeaway**: quantify improvements and key **lesson**.

• **Comparison Questions**  
  Respond with a short bullet list of the **key differences** only—no extra context, no examples, just the essentials.

• **Coding Questions**  
  1. **Reasoning**: brief explanation of your approach.  
  2. **Code**: present the full solution with detailed comments explaining each line and why each variable exists.  
  3. **Complexity**: state the time and space complexity.

**Always**  
- Start **directly** with your first content word.  
- Keep it **direct**, **accurate**, **to the point**—no fluff.  
- **Bold** every crucial term.  
- Change up phrasing and order so each answer feels fresh.
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
