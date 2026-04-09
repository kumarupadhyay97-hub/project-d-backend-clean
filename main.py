from fastapi import FastAPI
import requests
from datetime import datetime, timedelta
import os

app = FastAPI()

API_KEY = os.getenv("API_KEY")

# 🌍 COUNTRY LIST (for tagging only)
COUNTRIES = [
    "Nigeria","Kenya","South Africa","Egypt","Ethiopia","Ghana","Tanzania","Uganda",
    "Algeria","Morocco","Sudan","Angola","Mozambique","Zambia","Zimbabwe",
    "Senegal","Tunisia","Libya","Mali","Niger","Chad","Somalia","Namibia",
    "Botswana","Rwanda","Burundi","Malawi","Sierra Leone","Liberia","Togo",
    "Benin","Eritrea","Gambia","Gabon","Congo","DR Congo",
    "Djibouti","Lesotho","Eswatini","Guinea","Madagascar",
    "Mauritania","Seychelles","Comoros","Cape Verde","Cameroon"
]

def detect_country(title):
    for c in COUNTRIES:
        if c.lower() in title.lower():
            return c
    return "Africa"

def get_color(title):
    t = title.lower()

    if any(w in t for w in ["war","attack","conflict","military"]):
        return "red"
    elif any(w in t for w in ["tension","protest","crisis"]):
        return "orange"
    elif any(w in t for w in ["agreement","talks","meeting"]):
        return "blue"
    elif any(w in t for w in ["economy","investment","growth"]):
        return "green"
    elif any(w in t for w in ["policy","government","law"]):
        return "grey"
    else:
        return "white"


@app.get("/")
def fetch_news():

    if not API_KEY:
        return {"error": "API_KEY not set"}

    now = datetime.utcnow()
    past = now - timedelta(hours=24)
    from_time = past.strftime("%Y-%m-%dT%H:%M:%SZ")

    # 🔥 SINGLE STRONG QUERY
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q=Africa"
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

    for a in articles:
        title = a.get("title")
        link = a.get("url")
        time = a.get("publishedAt")

        if not title or not link:
            continue

        results.append({
            "title": title,
            "country": detect_country(title),
            "color": get_color(title),
            "timestamp": time,
            "source_url": link
        })

    return results