from fastapi import FastAPI
import requests
from datetime import datetime, timedelta
import os

app = FastAPI()

API_KEY = os.getenv("API_KEY")
print("DEBUG API_KEY:", API_KEY)

# 🌍 ALL AFRICAN COUNTRIES
COUNTRIES = [
    "Nigeria","Kenya","South Africa","Egypt","Ethiopia","Ghana","Tanzania","Uganda",
    "Algeria","Morocco","Sudan","Angola","Mozambique","Zambia","Zimbabwe",
    "Senegal","Tunisia","Libya","Mali","Niger","Chad","Somalia","Namibia",
    "Botswana","Rwanda","Burundi","Malawi","Sierra Leone","Liberia","Togo",
    "Benin","Eritrea","Gambia","Gabon","Republic of the Congo","DR Congo",
    "Djibouti","Lesotho","Eswatini","Guinea","Guinea-Bissau","Madagascar",
    "Mauritania","Seychelles","Comoros","Cape Verde","Central African Republic",
    "Equatorial Guinea","South Sudan","Burkina Faso","Ivory Coast","Cameroon"
]

# 🎨 COLOR LOGIC
def get_color(title):
    title = title.lower()

    if any(w in title for w in ["war", "attack", "conflict", "killed", "military", "violence"]):
        return "red"
    elif any(w in title for w in ["tension", "protest", "crisis", "dispute", "threat"]):
        return "orange"
    elif any(w in title for w in ["agreement", "talks", "meeting", "cooperation", "deal"]):
        return "blue"
    elif any(w in title for w in ["economy", "growth", "investment", "development"]):
        return "green"
    elif any(w in title for w in ["policy", "government", "law", "bill"]):
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

    all_results = []

    # 🔥 MULTI-COUNTRY FETCH
    for country in COUNTRIES:

        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={country}"
            f"&from={from_time}"
            f"&sortBy=publishedAt"
            f"&language=en"
            f"&pageSize=3"
            f"&apiKey={API_KEY}"
        )

        try:
            response = requests.get(url)
            data = response.json()
            articles = data.get("articles", [])

            for article in articles:
                title = article.get("title")
                link = article.get("url")
                published = article.get("publishedAt")

                if not title or not link:
                    continue

                all_results.append({
                    "title": title,
                    "country": country,
                    "color": get_color(title),
                    "timestamp": published,
                    "source_url": link
                })

        except:
            continue  # skip failed country

    return all_results