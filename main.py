from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# 🔥 CORS (REQUIRED)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "2a4405b3b2644a0fbfef25724a5ac90d"

# 🌍 ALL 54 AFRICAN COUNTRIES
AFRICA_COUNTRIES = [
    "Algeria","Angola","Benin","Botswana","Burkina Faso","Burundi",
    "Cabo Verde","Cameroon","Central African Republic","Chad","Comoros",
    "Democratic Republic of the Congo","Republic of the Congo","Djibouti",
    "Egypt","Equatorial Guinea","Eritrea","Eswatini","Ethiopia","Gabon",
    "Gambia","Ghana","Guinea","Guinea-Bissau","Ivory Coast","Kenya",
    "Lesotho","Liberia","Libya","Madagascar","Malawi","Mali","Mauritania",
    "Mauritius","Morocco","Mozambique","Namibia","Niger","Nigeria","Rwanda",
    "Sao Tome and Principe","Senegal","Seychelles","Sierra Leone","Somalia",
    "South Africa","South Sudan","Sudan","Tanzania","Togo","Tunisia",
    "Uganda","Zambia","Zimbabwe"
]

# 🌍 REGION KEYWORDS
AFRICA_REGIONS = [
    "africa", "african", "sahel", "horn of africa",
    "west africa", "east africa", "north africa",
    "central africa", "southern africa"
]

# 🎨 FINAL COLOR SYSTEM (STRONG + COMPLETE)
def get_color(text):
    text = text.lower()

    # 🔴 Conflict / escalation
    if any(w in text for w in [
        "war","attack","conflict","military","violence",
        "airstrike","clash","rebels","fighting","bomb"
    ]):
        return "red"

    # 🟠 Tension / instability
    elif any(w in text for w in [
        "tension","protest","crisis","warning","sanction",
        "unrest","strike","pressure"
    ]):
        return "orange"

    # 🟢 Cooperation / agreement
    elif any(w in text for w in [
        "agreement","cooperation","deal","partnership",
        "joint","collaboration","aid","support","funding"
    ]):
        return "green"

    # 🔵 Diplomacy / routine
    elif any(w in text for w in [
        "meeting","talks","discussion","summit",
        "visit","delegation","conference"
    ]):
        return "blue"

    # ⚫ Domestic / economy
    elif any(w in text for w in [
        "policy","economy","budget","finance",
        "inflation","growth","tax","investment"
    ]):
        return "grey"

    # ⬜ Everything else (NOISE)
    else:
        return "white"


# 🌍 COUNTRY DETECTION
def detect_country(text):
    text = text.lower()
    for country in AFRICA_COUNTRIES:
        if country.lower() in text:
            return country
    return "Africa"


@app.get("/")
def fetch_news():

    # 🔥 BROAD QUERY (ENSURES COVERAGE)
    query = "Africa OR African OR Nigeria OR Kenya OR Sudan OR Ethiopia OR Congo OR South Africa"

    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=100&apiKey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    if data.get("status") != "ok":
        return {"error": data}

    articles = data.get("articles", [])
    results = []

    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")

        full_text = f"{title} {description}".lower()

        # 🔥 FILTER (AFRICA ONLY)
        if not (
            any(country.lower() in full_text for country in AFRICA_COUNTRIES)
            or any(region in full_text for region in AFRICA_REGIONS)
        ):
            continue

        signal = {
            "title": title,
            "country": detect_country(full_text),
            "color": get_color(full_text),
            "timestamp": article.get("publishedAt", ""),
            "source_url": article.get("url", ""),
            "image_url": article.get("urlToImage", "")
        }

        results.append(signal)

    return results