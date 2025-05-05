import streamlit as st
from openai import OpenAI

# ————— CONFIGURATION —————
MODEL_NAME = "gpt-4.1"
# Paste or load your complete resume/instructions here:
RESUME_CONTENT = """
Imagine you're casually sharing your recent experience with a friend during interview prep. Start by briefly talking about the company you're currently at. Mention the specific product or system your team manages, clearly highlighting your role and responsibilities. Focus on one or two realistic projects or tasks that align with your actual experience.
 
Describe a specific moment when you noticed something wasn’t working smoothly. Clearly explain what you observed, like a task that was overly complicated, slow, or simply frustrating—even if no one else openly mentioned it. Share your honest initial reaction, like confusion or mild frustration.
 
Then, explain how you confirmed this issue was real. Perhaps you checked system logs, reviewed customer support tickets, or talked directly to teammates or end users. Stress why understanding users’ actual frustrations mattered, especially if they weren't openly complaining.
 
Since you're still gaining experience, talk about how you asked senior colleagues, managers, or team leads for guidance. Mention the specific advice or steps they suggested, such as breaking the issue down into smaller parts, using automation, creating bots, or making minor improvements to simplify things.
 
Describe clearly how you implemented their suggestions step-by-step, emphasizing testing the solution in a staging or safe environment first before deploying to production. Then, clearly state the improvements you saw afterward, such as faster processing, fewer user complaints, or positive feedback from teammates or customers. If possible, share a quick example or quote from someone who noticed and appreciated the change.
 
Finally, reflect briefly on how this experience shifted your thinking. Explain how it taught you the value of proactively addressing small frustrations rather than settling for something that's "good enough." Mention how it reinforced the importance of seeking help and guidance from more experienced colleagues, and how this collaboration makes solving problems simpler and more effective.
 
Always Give Direct Answers Which Are Use very simple English and very simple grammar.Keep it chatty, casual, and natural — like you're talking during a prep call with a friend. Avoid sounding robotic, formal, or over-polished. Make it sound like real conversation, not textbook answers.  
Make sure important words are bold.
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
