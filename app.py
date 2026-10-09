import streamlit as st
from ask import answer

st.set_page_config(page_title="Kali Troubleshooter", page_icon="🐉", layout="centered")

st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}
.hero h1 {font-size: 2.3rem; margin-bottom: 0;
  background: linear-gradient(90deg,#7C5CFF,#22D3EE);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.hero p {color: #9AA4B8; margin-top: .25rem; margin-bottom: 1.5rem;}
div[data-testid="stChatMessage"] {border-radius: 14px; padding: .6rem .9rem;}
div.stButton > button {border-radius: 999px; border: 1px solid #2A3550;
  background: #131A2A; color: #E6EAF2;}
div.stButton > button:hover {border-color: #7C5CFF; color: #7C5CFF;}
</style>
<div class="hero">
  <h1>Kali Troubleshooter</h1>
  <p>Answers grounded in the official Kali docs, with sources.</p>
</div>
""", unsafe_allow_html=True)

EXAMPLES = [
    "msfdb init fails and postgresql is not running",
    "apt says missing key which is needed to verify signature",
    "wlan0 does not show up after plugging in my usb adapter",
    "my live USB starts but changes disappear after every reboot",
]

if "messages" not in st.session_state:
    st.session_state.messages = []

def run(question):
    st.session_state.messages.append({"role": "user", "content": question})
    try:
        with st.spinner("Searching the Kali docs..."):
            text, sources = answer(question)
    except Exception as e:
        text, sources = f"Something went wrong: {e}", []
    st.session_state.messages.append({"role": "assistant", "content": text, "sources": sources})

if not st.session_state.messages:
    st.caption("Try one of these:")
    cols = st.columns(2)
    for i, ex in enumerate(EXAMPLES):
        if cols[i % 2].button(ex, key=f"ex{i}", use_container_width=True):
            run(ex)
            st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🧑‍💻" if m["role"] == "user" else "🐉"):
        st.markdown(m["content"])
        if m.get("sources"):
            with st.expander("Sources used"):
                for n, s in enumerate(m["sources"], 1):
                    st.markdown(f"**[{n}]** `{s}`")

if prompt := st.chat_input("Describe your Kali problem..."):
    run(prompt)
    st.rerun()