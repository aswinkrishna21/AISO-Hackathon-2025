"""
Text-only simulation for Elderly Voice Agent

This script lets you simulate the agent without audio/WebRTC by:
- Accepting natural-language commands in the terminal
- Having an LLM extract a structured action
- Calling the backend REST API to execute (send message or request a call)

Prereqs:
- Backend running (default http://localhost:8000)
- OPENAI_API_KEY set in environment

Usage:
  python simulate_text.py
  > send a message to John saying I miss you
  > call Sarah (voice)
  > make a video call to David
  > exit
"""

import os
import json
import sys
import time
from typing import Optional, Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore


SYSTEM_PROMPT = (
    "You are a command extractor for a voice agent helping elderly users. "
    "Given a user message, respond ONLY with minified JSON describing the action. "
    "Allowed actions: send_message, request_call, help. "
    "For send_message, include: contact (string), message (string). "
    "For request_call, include: contact (string), call_type ('voice' or 'video'). "
    "If ambiguous, choose action 'help' and include 'reason'. "
    "Return strictly a single JSON object with no extra text."
)


def ensure_openai():
    if OpenAI is None:
        print("ERROR: openai package not available. Install 'openai>=1.0.0'.", file=sys.stderr)
        sys.exit(1)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    return OpenAI(api_key=api_key)


def extract_command(client, text: str) -> Optional[dict]:
    try:
        completion = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        )
        content = completion.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as e:
        print(f"Failed to parse command via LLM: {e}")
        return None


def do_send_message(contact: str, message: str) -> Tuple[bool, str]:
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/messages/send",
            json={"contact": contact, "message": message},
            timeout=10,
        )
        if resp.ok and resp.json().get("status") == "success":
            return True, f"Message sent to {contact}."
        return False, f"Backend error: {resp.status_code} {resp.text}"
    except Exception as e:
        return False, f"Request failed: {e}"


def do_request_call(contact: str, call_type: str) -> Tuple[bool, str]:
    call_type = call_type if call_type in ("voice", "video") else "voice"
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/calls/request",
            json={"contact": contact, "type": call_type},
            timeout=10,
        )
        if resp.ok and resp.json().get("status") == "success":
            room_url = resp.json().get("room_url")
            return True, f"Call ({call_type}) requested with {contact}. Room: {room_url}"
        return False, f"Backend error: {resp.status_code} {resp.text}"
    except Exception as e:
        return False, f"Request failed: {e}"


def main():
    print("Text simulation started. Type natural commands, or 'exit' to quit.")
    print(f"Backend: {BACKEND_URL}")
    client = ensure_openai()

    while True:
        try:
            user = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user:
            continue
        if user.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break

        cmd = extract_command(client, user)
        if not cmd:
            print("Sorry, I couldn't understand that.")
            continue

        action = cmd.get("action")
        if action == "send_message":
            ok, msg = do_send_message(cmd.get("contact", ""), cmd.get("message", ""))
            print(msg)
        elif action == "request_call":
            ok, msg = do_request_call(cmd.get("contact", ""), cmd.get("call_type", "voice"))
            print(msg)
        elif action == "help":
            print("I need more details:")
            print(cmd.get("reason", "Ambiguous request"))
        else:
            print("I can send messages or request calls. Try e.g. 'Send a message to Emma saying hello'.")


if __name__ == "__main__":
    main()
