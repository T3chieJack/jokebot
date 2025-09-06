import os, sys, time, requests

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
if not WEBHOOK_URL:
    print("Missing DISCORD_WEBHOOK_URL", file=sys.stderr); sys.exit(1)

def get_joke():
    r = requests.get("https://icanhazdadjoke.com/",
                     headers={"Accept": "application/json"},
                     timeout=10)
    r.raise_for_status()
    return r.json().get("joke", "No joke found 🤷")

def post_discord(joke):
    payload = {
        "username": "Punchline",
        "embeds": [{
            "title": "😂 Here’s your daily joke",
            "description": f"> {joke}",
        }]
    }
    # Simple retry on 429/5xx
    for attempt in range(3):
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        if resp.status_code in (200, 204):
            return True
        if resp.status_code == 429 or 500 <= resp.status_code < 600:
            time.sleep(min(2 ** attempt, 8))
            continue
        print(f"Failed: {resp.status_code} {resp.text}", file=sys.stderr)
        return False
    print("Failed after retries", file=sys.stderr)
    return False

if __name__ == "__main__":
    joke = get_joke()
    ok = post_discord(joke)
    sys.exit(0 if ok else 1)

