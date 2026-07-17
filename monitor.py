import hashlib
from bs4 import BeautifulSoup
import os
from pathlib import Path

import requests

URL = "https://carnaldish.bigcartel.com/"
STATE_FILE = Path("website_hash.txt")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")

response = requests.get(
    URL,
    timeout=30,
    headers={"User-Agent": "Mozilla/5.0 Website Change Monitor"},
)
response.raise_for_status()

current_hash = hashlib.sha256(response.content).hexdigest()

if not STATE_FILE.exists():
    STATE_FILE.write_text(current_hash)
    print("First check complete. Baseline saved.")

else:
    previous_hash = STATE_FILE.read_text().strip()

    if current_hash != previous_hash:
        print("The website changed!")

        if not NTFY_TOPIC:
            raise RuntimeError("NTFY_TOPIC is not configured.")

        notification = requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data="Something changed on the Carnal Dish website!",
            headers={
                "Title": "Carnal Dish changed",
                "Click": URL,
                "Priority": "high",
                "Tags": "cookie,rotating_light",
            },
            timeout=30,
        )
        notification.raise_for_status()

        STATE_FILE.write_text(current_hash)
        print("Notification sent and new version saved.")

    else:
        print("No website changes detected.")
