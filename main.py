import requests
import time
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load configuration from config.json
try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("Error: config.json not found")
    exit(1)
except json.JSONDecodeError:
    print("Error: Invalid JSON in config.json")
    exit(1)

# Configuration variables
MEMOS_API_URL = config.get('MEMOS_API_URL')
DISCORD_WEBHOOK_URL = config.get('DISCORD_WEBHOOK_URL')
MEMOS_ACCESS_TOKEN = config.get('MEMOS_ACCESS_TOKEN')
AVATAR_URL = config.get('AVATAR_URL', 'https://your-optional-avatar-url.png')  # Fallback if not specified

# Validate configuration
if not all([MEMOS_API_URL, DISCORD_WEBHOOK_URL]):
    print("Error: Missing required configuration values in config.json")
    exit(1)

# Set up session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=1)
session.mount("https://", HTTPAdapter(max_retries=retries))

def get_new_memos():
    headers = {"Authorization": f"Bearer {MEMOS_ACCESS_TOKEN}"} if MEMOS_ACCESS_TOKEN else {}
    try:
        response = session.get(MEMOS_API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        print("API Response:", data)  # Debug
        return data
    except requests.RequestException as e:
        print(f"Failed to fetch memos: {e}")
        return {"memos": []}

def send_to_discord(content):
    payload = {
        "content": content,
        "username": "Memos Bot",
        "avatar_url": AVATAR_URL
    }
    try:
        response = session.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Sent to Discord:", content)  # Debug
    except requests.RequestException as e:
        print(f"Failed to send to Discord: {e}")

def main():
    last_memo_time = None
    send_to_discord("Memo2Discord started!")  # Debug
    while True:
        memos_data = get_new_memos()
        memo_list = memos_data.get("memos", [])  # Use "memos" key
        print("Memos found:", len(memo_list))  # Debug
        for memo in memo_list:
            memo_time = memo.get("createTime")
            print(f"Processing memo time: {memo_time}, Last time: {last_memo_time}")  # Debug
            if last_memo_time is None or memo_time > last_memo_time:
                content = memo.get("content", "No content")
                print(f"Sending memo: {content}")  # Debug
                send_to_discord(content)  # Send only the content
                last_memo_time = memo_time
        time.sleep(60)

if __name__ == "__main__":
    main()