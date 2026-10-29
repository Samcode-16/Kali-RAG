
from dotenv import load_dotenv
load_dotenv()

import os
from google import genai
from google.genai import types
from openai import OpenAI

from retrieval import chunks, hybrid_top, THRESHOLD


# Gemini configuration
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
client = genai.Client()


# Groq configuration
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
GROQ_BASE_URL = os.environ.get(
    "GROQ_BASE_URL",
    "https://api.groq.com/openai/v1",
)


SYSTEM = """You are a Kali Linux troubleshooting assistant.
Answer ONLY using the numbered sources provided. Do not use outside knowledge.
Cite the sources you use like [1] or [2] after each claim.
Only give commands that appear in the sources.
If the sources do not contain enough information to answer, reply exactly:
I don't know based on the Kali docs.
Keep the answer short and practical."""


def call_gemini(system, user):
    response = client.models.generate_content(
        model=MODEL,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.0,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")

    return response.text


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

    return text


def call_llm(system, user):
    # Try Gemini first.
    try:
        print("Using Gemini...")
        return call_gemini(system, user)

    except Exception as gemini_error:
        print(f"Gemini failed: {gemini_error}")

    # If Gemini fails, try Groq.
    try:
        print("Falling back to Groq...")
        return call_groq(system, user)

    except Exception as groq_error:
        print(f"Groq failed: {groq_error}")
        raise RuntimeError(
            "Both Gemini and Groq failed. Check the terminal logs."
        ) from groq_error


def answer(question):
    best, top = hybrid_top(question, k=8)

    if best < THRESHOLD:
        return "I don't know. Nothing in my Kali docs matches this well.", []

    sources = [chunks[i] for i in top]

    # DEBUG: Inspect the retrieved documentation chunks
    print("\n========== RETRIEVED CONTEXT ==========")

    for n, (folder, text) in enumerate(sources, 1):
        print(f"\n[{n}] Folder: {folder}")
        print(text[:2000])

    print("\n========== END CONTEXT ==========\n")

    context = "\n\n".join(
        f"[{n}] ({folder})\n{text}"
        for n, (folder, text) in enumerate(sources, 1)
    )

    user = f"SOURCES:\n{context}\n\nQUESTION: {question}"

    response = call_llm(SYSTEM, user)
    return response, [folder for folder, _ in sources]


if __name__ == "__main__":
    while True:
        question = input(
            "\nAsk a Kali question (or quit): "
        ).strip()

        if question.lower() == "quit":
            break

        if not question:
            continue

        try:
            response, cited = answer(question)
            print("\n" + response)

            if cited:
                print(
                    "\nSources retrieved:",
                    ", ".join(
                        f"[{n}] {folder}"
                        for n, folder in enumerate(cited, 1)
                    ),
                )

        except Exception as error:
            print(f"\nCould not generate an answer: {error}")
