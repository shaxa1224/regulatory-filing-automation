import os

from dotenv import load_dotenv
from groq import Groq


def main() -> int:
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env")
        return 1

    required_model = "llama-3.3-70b-versatile"
    configured_model = os.getenv("GROQ_MODEL")
    if configured_model and configured_model != required_model:
        print(f"⚠️ GROQ_MODEL is set to {configured_model!r}; expected {required_model!r}")

    print("✅ API key loaded")

    client = Groq(api_key=api_key)

    print("⏳ Calling Groq API...")
    response = client.chat.completions.create(
        model=required_model,
        messages=[{"role": "user", "content": "Say hello and confirm your model name."}],
        temperature=0.3,
        max_tokens=100,
    )

    print(f"✅ Success: {response.choices[0].message.content}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
