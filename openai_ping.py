"""Simple OpenAI connectivity smoke test.

Sends a minimal 'Hi' prompt to the gpt-4o-mini model using the new Responses
endpoint first (preferred in recent OpenAI API), falling back to the legacy
chat.completions API if needed.

Usage (PowerShell):
  $env:OPENAI_API_KEY="sk-..."  # set your key
  python openai_ping.py

Exit codes:
  0 => success
  1 => missing API key
  2 => API call failed
"""
from __future__ import annotations
import os, sys, json
from typing import Optional
from openai import OpenAI

MODEL_NAME = "gpt-4o-mini"


def extract_text_from_responses(resp) -> str:
    """Try to extract contiguous text from a Responses endpoint reply.
    The structure may evolve; we defensively traverse known fields.
    """
    if hasattr(resp, "output_text") and resp.output_text:
        return resp.output_text
    parts: list[str] = []
    output = getattr(resp, "output", None)
    if output:
        for item in output:
            content = getattr(item, "content", [])
            for chunk in content:
                text = getattr(chunk, "text", None)
                if text:
                    parts.append(text)
    return "".join(parts).strip()


def call_responses(client: OpenAI) -> Optional[str]:
    """Call the new Responses endpoint; return text or None if it fails."""
    try:
        resp = client.responses.create(
            model=MODEL_NAME,
            input=[{"role": "user", "content": "Hi"}],
            temperature=0.2,
        )
        text = extract_text_from_responses(resp)
        if not text:
            raise ValueError("Empty text from responses endpoint")
        print("[responses] success:\n" + text)
        return text
    except Exception as e:
        print(f"[responses] failed: {type(e).__name__}: {e}")
        return None


def call_chat_completions(client: OpenAI) -> Optional[str]:
    """Fallback to legacy chat.completions API."""
    try:
        chat = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Hi"}],
            temperature=0.2,
        )
        text = chat.choices[0].message.content.strip()
        print("[chat.completions] success:\n" + text)
        return text
    except Exception as e:
        print(f"[chat.completions] failed: {type(e).__name__}: {e}")
        return None


def main() -> int:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        return 1

    client = OpenAI(api_key=api_key)

    # Try Responses first.
    text = call_responses(client)
    if not text:
        print("Falling back to chat.completions ...")
        text = call_chat_completions(client)

    if not text:
        print("ERROR: No successful response from any endpoint.")
        return 2

    # Basic sanity check: ensure some conversational phrasing.
    if len(text) < 2:
        print("WARNING: Response very short; may indicate an issue.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
