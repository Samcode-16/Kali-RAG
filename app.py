
import streamlit as st
from ask import answer

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Kali Troubleshooter",
    page_icon="🐉",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# Styling
# --------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --accent: #8B7CFF;
        --cyan: #22D3EE;
        --muted: #94A3B8;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 7rem;
    }

    .hero {
        padding: 1rem 0 1.5rem 0;
    }

    .hero h1 {
        font-size: clamp(2rem, 5vw, 2.8rem);
        font-weight: 750;
        letter-spacing: -1.2px;
        margin-bottom: 0.3rem;
        background: linear-gradient(
            90deg, #9B8AFF, #22D3EE
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero p {
        color: var(--muted);
        font-size: 1rem;
        margin-top: 0;
    }

    .eyebrow {
        color: #9B8AFF;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    div[data-testid="stChatMessage"] {
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 16px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.8rem;
    }

    div.stButton > button {
        width: 100%;
        min-height: 3rem;
        border: 1px solid #303B55;
        border-radius: 12px;
        background: #141C30;
        color: #E6EAF2;
        text-align: left;
        transition: border-color 0.2s, background 0.2s;
    }

    div.stButton > button:hover {
        border-color: #8B7CFF;
        background: #1A2340;
        color: #FFFFFF;
    }

    div[data-testid="stChatInput"] {
        border-color: #394563;
        border-radius: 16px;
    }

    div[data-testid="stExpander"] {
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 12px;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(148, 163, 184, 0.15);
    }

    .footer-note {
        color: #8290AA;
        font-size: 0.78rem;
        text-align: center;
        padding-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Example questions
# --------------------------------------------------
EXAMPLES = {
    "📦 Packages & APT": [
        "apt says a missing key is needed to verify a signature",
        "How do I fix broken packages in Kali Linux?",
    ],
    "📡 Networking": [
        "wlan0 does not show up after plugging in my USB adapter",
        "How do I diagnose a network interface that is down?",
    ],
    "⚙️ Services & Tools": [
        "msfdb init fails and PostgreSQL is not running",
        "How do I troubleshoot a systemd service that fails to start?",
    ],
    "💾 Live USB": [
        "My live USB starts but changes disappear after every reboot",
        "How do I troubleshoot a Kali Live USB boot problem?",
    ],
}

# --------------------------------------------------
# Session state
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


def new_chat():
    st.session_state.messages = []
    st.session_state.pending_question = None



def run_question(question):
    question = question.strip()
    if not question:
        return

    # Save the user's question.
    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    # Display the question immediately.
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(question)

    # Display a loading indicator while generating the answer.
    with st.chat_message("assistant", avatar="🐉"):
        with st.spinner("Searching documentation and generating answer..."):
            try:
                response, sources = answer(question)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": sources or [],
                })

            except Exception:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (
                        "I couldn't complete the search. Check your API "
                        "configuration and application logs, then try again."
                    ),
                    "sources": [],
                    "error": True,
                })

    # Render the completed conversation.
    st.rerun()



def render_sources(sources):
    with st.expander(f"📚 Sources used ({len(sources)})"):
        for index, source in enumerate(sources, start=1):
            source_text = str(source)

            # If a source is a URL, make it clickable.
            if source_text.startswith(("https://", "http://")):
                st.markdown(
                    f"**[{index}]** [{source_text}]({source_text})"
                )
            else:
                st.markdown(f"**[{index}]** `{source_text}`")


# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.markdown("## 🐉 Kali Troubleshooter")
    st.caption("Your documentation-grounded troubleshooting assistant")

    if st.button("＋  New conversation", use_container_width=True):
        new_chat()
        st.rerun()

    st.divider()

    st.markdown("### Troubleshooting areas")
    st.caption("Choose a starting point")

    for category, questions in EXAMPLES.items():
        with st.expander(category):
            for index, question in enumerate(questions):
                if st.button(
                    question,
                    key=f"sidebar_{category}_{index}",
                    use_container_width=True,
                ):
                    st.session_state.pending_question = question
                    st.rerun()

    st.divider()
    st.caption("Powered by your custom hybrid RAG pipeline")
    st.caption("Gemini · Semantic search · BM25")


# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">LINUX SUPPORT · RAG</div>
        <h1>Kali Troubleshooter</h1>
        <p>
            Diagnose Kali Linux issues with answers grounded
            in retrieved documentation and source references.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Welcome screen
# --------------------------------------------------
if not st.session_state.messages:
    st.markdown("### What are you troubleshooting?")
    st.write(
        "Select a common issue or describe your problem below. "
        "Include the exact error message when possible."
    )

    cols = st.columns(2)

    for index, (category, questions) in enumerate(EXAMPLES.items()):
        with cols[index % 2]:
            with st.container(border=True):
                st.markdown(f"**{category}**")
                st.caption(questions[0])

                if st.button(
                    "Try this example →",
                    key=f"welcome_{index}",
                    use_container_width=True,
                ):
                    st.session_state.pending_question = questions[0]
                    st.rerun()

    st.markdown(
        """
        <p class="footer-note">
            Tip: Share the command you ran and the complete error output.
        </p>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# Conversation history
# --------------------------------------------------
for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "🐉"

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

        if message.get("error"):
            st.warning(
                "If this persists, inspect the application terminal "
                "for the underlying exception."
            )

        if message.get("sources"):
            render_sources(message["sources"])


# --------------------------------------------------
# Question input and example-question handling
# --------------------------------------------------

# Process questions selected from the sidebar or welcome screen.
if st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None
    run_question(question)

# Process questions typed into the chat box.
if prompt := st.chat_input("Describe your Kali problem..."):
    run_question(prompt)