
from dotenv import load_dotenv
load_dotenv()

import os

from google import genai
from google.genai import types
from openai import OpenAI

from retrieval import chunks, hybrid_top, THRESHOLD


# =====================================================
# CONFIGURATION
# =====================================================

GEMINI_MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)

GROQ_MODEL = os.environ.get(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

GROQ_BASE_URL = os.environ.get(
    "GROQ_BASE_URL",
    "https://api.groq.com/openai/v1"
)

REFUSAL_MESSAGE = "I don't know based on the Kali docs."


# =====================================================
# SYSTEM INSTRUCTION
# =====================================================

SYSTEM = """
You are a Kali Linux troubleshooting assistant.

Follow these rules strictly:

1. Answer ONLY using the numbered sources provided.
2. Do not use outside knowledge or invent missing information.
3. Cite sources using their numbers, such as [1] or [2].
4. Place citations after the claims they support.
5. Only provide commands that explicitly appear in the sources.
6. Do not combine commands from unrelated contexts.
7. If the sources do not contain enough relevant information
   to answer the question, reply exactly:

   I don't know based on the Kali docs.

8. Keep answers short, clear, and practical.
"""


# =====================================================
# GEMINI
# =====================================================

def call_gemini(system, user):

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.0,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")

    return response.text.strip()


# =====================================================
# GROQ FALLBACK
# =====================================================

def call_groq(system, user):

    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    groq_client = OpenAI(
        api_key=api_key,
        base_url=GROQ_BASE_URL,
        timeout=30.0,
        max_retries=0,
    )

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.0,
    )

    text = response.choices[0].message.content

    if not text:
        raise RuntimeError("Groq returned an empty response")

    return text.strip()


# =====================================================
# LLM PROVIDER SELECTION
# =====================================================

def call_llm(system, user):

    # Try Gemini first.
    try:
        print("Using Gemini...")
        return call_gemini(system, user)

    except Exception as gemini_error:
        print(f"Gemini failed: {gemini_error}")

    # Fall back to Groq if Gemini fails.
    try:
        print("Falling back to Groq...")
        return call_groq(system, user)

    except Exception as groq_error:
        print(f"Groq failed: {groq_error}")

        raise RuntimeError(
            "Both Gemini and Groq failed. Check your API configuration."
        ) from groq_error


# =====================================================
# RAG ANSWER GENERATION
# =====================================================

def answer(question):

    question = question.strip()

    if not question:
        return REFUSAL_MESSAGE, []

    # Retrieve the top 5 relevant chunks.
    best, top = hybrid_top(question, k=5)

    print(f"\nBest dense similarity: {best:.4f}")

    # Reject questions with insufficient retrieval similarity.
    if best < THRESHOLD or not top:
        print("Retrieval rejected: similarity below threshold.")
        return REFUSAL_MESSAGE, []

    
    sources = [chunks[i] for i in top]

    # Inspect retrieved chunks
    print("\n========== RETRIEVED CONTEXT ==========")

    for n, chunk in enumerate(sources, 1):
        print(f"\n[{n}] Folder: {chunk['folder']}")
        print(f"Title: {chunk['title']}")
        print(f"Heading: {chunk['heading']}")
        print(chunk['content'][:2000])

    print("\n========== END CONTEXT ==========\n")

    # Build numbered context
    context = "\n\n".join(
        f"[{n}] "
        f"Document: {chunk['folder']}\n"
        f"Title: {chunk['title']}\n"
        f"Section: {chunk['heading']}\n"
        f"{chunk['content']}"
        for n, chunk in enumerate(sources, 1)
    )

    user_prompt = f"""
SOURCES:

{context}

QUESTION:
{question}

Answer using only the supplied sources.
Cite the sources supporting your answer.
"""

    response = call_llm(SYSTEM, user_prompt)

    return response, [chunk["folder"] for chunk in sources]


# =====================================================
# TERMINAL INTERFACE
# =====================================================

if __name__ == "__main__":

    print("Kali Linux Troubleshooting Assistant")
    print("Type 'quit' to exit.")

    while True:

        question = input(
            "\nAsk a Kali question: "
        ).strip()

        if question.lower() == "quit":
            print("Exiting Kali-RAG...")
            break

        if not question:
            continue

        try:

            response, cited = answer(question)

            print("\n========== ANSWER ==========")
            print(response)

            if cited:
                print("\n========== SOURCES ==========")

                for n, folder in enumerate(cited, 1):
                    print(f"[{n}] {folder}")

        except Exception as error:

            print(f"\nCould not generate an answer: {error}")
