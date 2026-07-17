import hashlib
import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://carnaldish.bigcartel.com/"
STATE_FILE = Path("website_hash.txt")
NTFY_TOPIC = os.environ["NTFY_TOPIC"]

headers = {
    "User-Agent": "Mozilla/5.0 (Website Monitor)"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

# Only monitor the visible text on the page
soup = BeautifulSoup(response.text, "html.parser")

# Remove things that change frequently but aren't meaningful
for tag in soup(["script", "style", "noscript"]):
    tag.decompose()

visible_text = " ".join(soup.stripped_strings)

current_hash = hashlib.sha256(visible_text.encode()).hexdigest()

if not STATE_FILE.exists():
    STATE_FILE.write_text(current_hash)
    print("First check complete. Baseline saved.")
else:
    previous_hash = STATE_FILE.read_text().strip()

    if current_hash != previous_hash:
        print("Website changed!")

        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data="🍪 Carnal Dish website changed!\nhttps://carnaldish.bigcartel.com/",
            headers={
                "Title": "Carnal Dish Update",
                "Priority": "high",
                "Tags": "cookie,bell",
            },
            timeout=30,
        )

        STATE_FILE.write_text(current_hash)
        print("Notification sent.")

    else:
        print("No changes detected.")
