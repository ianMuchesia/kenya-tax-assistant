"""Milestone 4, step 2: call Gemini. Stays under the free limits, retries when told to wait, and saves every answer.

    python gemini.py "Say hello in one Swahili word"

Saved answers mean a rerun of the eval spends no requests: only new prompts go to Google.
The caller must mask private details first: this file sends exactly the text it is given.
"""

import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODEL = "gemini-3.1-flash-lite"     # free tier: 15 requests a minute, 500 a day
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
SECONDS_BETWEEN_CALLS = 4.5         # 60 / 15 = 4, plus a small margin
MAX_TRIES = 4
RETRY_WAIT = 15                     # seconds: 15, then 30, then 45
RETRY_CODES = [429, 500, 503]       # 429 = too many requests, 500 and 503 = Google's side had a problem


def load_api_key() -> str:
    """Read GEMINI_API_KEY from .env. The key travels in a header, never in the URL, so it can't end up in a log."""
    for line in (HERE / ".env").read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("GEMINI_API_KEY not found in .env")




class Gemini:
    def __init__(self, model: str = MODEL):
        self.model = model
        self.api_key = load_api_key()
        self.last_call_time = 0.0
        self.cache_path = HERE / "gemini_cache.jsonl"
        self.cache = {}
        if self.cache_path.exists():
            with self.cache_path.open(encoding="utf-8") as f:
                for line in f:
                    record = json.loads(line)
                    self.cache[record["key"]] = record["answer"]
                    
                    
    def wait_for_turn(self) -> None:
        """Sleep if the last call was too recent, so we never go over the per-minute limit."""
        seconds_since_last = time.time() - self.last_call_time
        if seconds_since_last < SECONDS_BETWEEN_CALLS:
            time.sleep(SECONDS_BETWEEN_CALLS - seconds_since_last)
        self.last_call_time = time.time()
        
        
        
    def send(self, system: str, prompt: str) -> str:
        """One real request to Google."""
        url = f"{BASE_URL}/{self.model}:generateContent"
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0},
        }
        body_bytes = json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json", "x-goog-api-key": self.api_key}
        request = urllib.request.Request(url, data=body_bytes, headers=headers)

        with urllib.request.urlopen(request, timeout=120) as response:
            answer = json.loads(response.read())

        text = ""
        for part in answer["candidates"][0]["content"]["parts"]:
            text = text + part["text"]
        return text
    
    
    
    def ask(self, system: str, prompt: str) -> str:
        """Saved answer if we have one; otherwise call Google, retrying if it asks us to wait."""
        text_to_hash = self.model + "\n" + system + "\n" + prompt
        key = hashlib.sha256(text_to_hash.encode("utf-8")).hexdigest()
        if key in self.cache:
            return self.cache[key]

        for attempt in range(1, MAX_TRIES + 1):
            self.wait_for_turn()
            try:
                answer = self.send(system, prompt)
                break
            except urllib.error.HTTPError as error:
                if error.code not in RETRY_CODES or attempt == MAX_TRIES:
                    raise
                wait = RETRY_WAIT * attempt
                print(f"Gemini said {error.code}: waiting {wait} seconds (try {attempt} of {MAX_TRIES})")
                time.sleep(wait)

        self.cache[key] = answer
        with self.cache_path.open("a", encoding="utf-8") as f:
            record = {"key": key, "answer": answer}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return answer
    
    
    
if __name__ == "__main__":
    prompt = sys.argv[1]
    gemini = Gemini()
    start_time = time.time()
    answer = gemini.ask("You are a helpful assistant. Keep answers short.", prompt)
    print(answer)
    print(f"({time.time() - start_time:.1f} seconds)")