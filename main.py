from fastapi import FastAPI
import requests
from datetime import datetime, timedelta
import os

app = FastAPI()

API_KEY = os.getenv("2a4405b3b2644a0fbfef25724a5ac90")

# 🌍 ALL AFRICAN COUNTRIES (keywords)
AFRICA_KEYWORDS = (
    "Africa OR Nigeria OR Kenya OR South Africa OR Egypt OR Ethiopia OR "
    "Ghana OR Tanzania OR Uganda OR Algeria OR Morocco OR Sudan OR Angola OR "
    "Mozambique OR Zambia OR Zimbabwe OR Senegal OR Tunisia OR Libya OR Mali OR "
    "Niger OR Chad OR Somalia OR Namibia OR Botswana OR Rwanda OR Burundi OR "
    "Malawi OR Sierra Leone OR Liberia OR Togo OR Benin OR Eritrea OR Gambia OR "
    "Gabon OR Congo OR DRC OR Djibouti OR Lesotho OR Eswatini OR Guinea OR "
    "Guinea-Bissau OR Madagascar OR Mauritania OR Seychelles OR Comoros OR Cape Verde"
)

# 🎨 COLOR LOGIC
def get_color(title):
    title = title.lower()

    if any(word in title for word in ["war", "attack", "conflict", "killed", "military", "violence"]):
        return "red"
    elif any(word in title for word in ["tension", "protest", "crisis", "dispute", "threat"]):
        return "orange"
    elif any(word in title for word in ["agreement", "talks", "meeting", "cooperation", "deal"]):
        return "blue"
    elif any(word in title for word in ["development", "growth", "economy", "investment"]):
        return "green"
    elif any(word in title for word in ["policy", "government", "bill", "law"]):
        return "grey"
    else:
        return "white"  # fallback (important)

@app.get("/")
def fetch_news():
    if not API_KEY:
        return {"error": "API_KEY not set"}

    # 🕒 LAST 24 HOURS
    now = datetime.utcnow()
    past = now - timedelta(hours=24)

    from_time = past.strftime("%Y-%m-%dT%H:%M:%SZ")

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={AFRICA_KEYWORDS}"
        f"&from={from_time}"
        f"&sortBy=publishedAt"
        f"&language=en"
        f"&pageSize=100"
        f"&apiKey={API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    articles = data.get("articles", [])

    results = []

    for article in articles:
        title = article.get("title")
        url = article.get("url")
        published = article.get("publishedAt")

        if not title or not url:
            continue

        results.append({
            "title": title,
            "country": "Africa",
            "color": get_color(title),
            "timestamp": published,
            "source_url": url
        })

    return results