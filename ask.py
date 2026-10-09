from retrieval import chunks, hybrid_top, THRESHOLD

PROVIDER = "anthropic"   

SYSTEM = """You are a Kali Linux troubleshooting assistant.
Answer ONLY using the numbered sources provided. Do not use outside knowledge.
Cite the sources you use like [1] or [2] after each claim.
Only give commands that appear in the sources.
If the sources do not contain enough information to answer, reply exactly:
I don't know based on the Kali docs.
Keep the answer short and practical."""

def call_llm(system, user):
    if PROVIDER == "anthropic":
        import anthropic
        client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from the environment
        msg = client.messages.create(
            model="claude-sonnet-5-5", max_tokens=800, system=system,
            messages=[{"role": "user", "content": user}])
        return msg.content[0].text
    import ollama
    r = ollama.chat(model="llama3.2", messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": user}])
    return r["message"]["content"]

def answer(question):
    best, top = hybrid_top(question, k=3)
    if best < THRESHOLD:
        return "I don't know. Nothing in my Kali docs matches this well.", []
    sources = [chunks[i] for i in top]
    context = "\n\n".join(f"[{n}] ({folder})\n{text}"
                          for n, (folder, text) in enumerate(sources, 1))
    user = f"SOURCES:\n{context}\n\nQUESTION: {question}"
    return call_llm(SYSTEM, user), [f for f, _ in sources]

if __name__ == "__main__":
    while True:
        q = input("\nAsk a Kali question (or quit): ").strip()
        if q.lower() == "quit":
            break
        text, cited = answer(q)
        print("\n" + text)
        if cited:
            print("\nSources retrieved:", ", ".join(f"[{n}] {c}" for n, c in enumerate(cited, 1)))