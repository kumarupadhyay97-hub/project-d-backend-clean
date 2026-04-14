from fastapi import FastAPI
from rss_fetcher import fetch_rss_news
import re
from collections import defaultdict

app = FastAPI()

# -------------------------------
# AFRICA COUNTRY MAP (FULL + DEMONYMS)
# -------------------------------
COUNTRY_MAP = {
    "algeria": "Algeria", "algerian": "Algeria",
    "angola": "Angola", "angolan": "Angola",
    "benin": "Benin", "beninese": "Benin",
    "botswana": "Botswana",
    "burkina faso": "Burkina Faso",
    "burundi": "Burundi", "burundian": "Burundi",
    "cameroon": "Cameroon", "cameroonian": "Cameroon",
    "cape verde": "Cape Verde",
    "central african republic": "Central African Republic",
    "chad": "Chad", "chadian": "Chad",
    "comoros": "Comoros",
    "congo": "Congo",
    "dr congo": "DR Congo",
    "ivory coast": "Ivory Coast",
    "cote d'ivoire": "Ivory Coast",
    "djibouti": "Djibouti",
    "egypt": "Egypt", "egyptian": "Egypt",
    "eritrea": "Eritrea",
    "ethiopia": "Ethiopia", "ethiopian": "Ethiopia",
    "gabon": "Gabon",
    "gambia": "Gambia",
    "ghana": "Ghana", "ghanaian": "Ghana",
    "guinea": "Guinea",
    "kenya": "Kenya", "kenyan": "Kenya",
    "lesotho": "Lesotho",
    "liberia": "Liberia",
    "libya": "Libya", "libyan": "Libya",
    "madagascar": "Madagascar",
    "malawi": "Malawi",
    "mali": "Mali",
    "mauritania": "Mauritania",
    "morocco": "Morocco", "moroccan": "Morocco",
    "mozambique": "Mozambique",
    "namibia": "Namibia",
    "niger": "Niger",
    "nigeria": "Nigeria", "nigerian": "Nigeria",
    "rwanda": "Rwanda",
    "senegal": "Senegal",
    "sierra leone": "Sierra Leone",
    "somalia": "Somalia",
    "south africa": "South Africa", "south african": "South Africa",
    "south sudan": "South Sudan",
    "sudan": "Sudan",
    "tanzania": "Tanzania", "tanzanian": "Tanzania",
    "togo": "Togo",
    "tunisia": "Tunisia",
    "uganda": "Uganda", "ugandan": "Uganda",
    "zambia": "Zambia",
    "zimbabwe": "Zimbabwe", "zimbabwean": "Zimbabwe"
}

# -------------------------------
# NOISE FILTER
# -------------------------------
BLOCK_KEYWORDS = [
    "sport", "football", "cricket", "match", "league",
    "coach", "tournament", "goal", "cup", "fifa",
    "nba", "tennis", "olympics", "player", "score",
    "trump", "russia", "ukraine", "israel", "iran",
    "celebrity", "movie", "film", "music"
]

# -------------------------------
# AFRICA CONTEXT CHECK
# -------------------------------
def is_africa_related(title):
    title = title.lower()
    africa_terms = [
        "africa", "african", "african union", "au",
        "lagos", "nairobi", "cairo", "johannesburg",
        "addis ababa", "accra", "dakar"
    ]
    return any(term in title for term in africa_terms)

# -------------------------------
# SOURCE TYPE + WEIGHT
# -------------------------------
def get_source_type(source_url):
    source_url = source_url.lower()

    if "gov" in source_url:
        return "government", 10
    if "reuters" in source_url:
        return "media", 7
    if "bbc" in source_url or "cnn" in source_url or "aljazeera" in source_url:
        return "media", 5

    return "media", 3

# -------------------------------
# SIGNAL CLASSIFICATION
# -------------------------------
def get_signal_color(title):
    title = title.lower()

    if any(w in title for w in ["war", "attack", "conflict", "military", "strike"]):
        return "red"
    if any(w in title for w in ["tension", "protest", "crisis", "clash"]):
        return "orange"
    if any(w in title for w in ["agreement", "deal", "talks", "visit", "summit"]):
        return "blue"
    if any(w in title for w in ["election", "president", "policy", "economy", "bank", "inflation"]):
        return "grey"

    return "grey"

# -------------------------------
# DETECT COUNTRY (FIXED)
# -------------------------------
def detect_country(title):
    title = title.lower()

    for key in COUNTRY_MAP:
        pattern = r"\b" + re.escape(key) + r"\b"
        if re.search(pattern, title):
            return COUNTRY_MAP[key]

    return None

# -------------------------------
# NOISE CHECK
# -------------------------------
def is_noise(title):
    title = title.lower()
    return any(word in title for word in BLOCK_KEYWORDS)

# -------------------------------
# REMOVE DUPLICATES
# -------------------------------
def remove_duplicates(results):
    seen = set()
    unique = []

    for item in results:
        key = item["title"].lower()[:60]

        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique

# -------------------------------
# GROUP BY DATE (TIMELINE SYSTEM)
# -------------------------------
def group_by_date(results):
    grouped = defaultdict(list)

    month_map = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }

    for item in results:
        timestamp = item.get("timestamp", "")

        if timestamp:
            try:
                parts = timestamp.split()
                day = parts[1]
                month = parts[2]
                year = parts[3]
                date = f"{year}-{month_map.get(month, '00')}-{day}"
            except:
                date = "Unknown"
        else:
            date = "Unknown"

        grouped[date].append(item)

    # SORT INSIDE EACH DAY
    for date in grouped:
        grouped[date].sort(key=lambda x: x["timestamp"], reverse=True)

    # SORT DAYS
    return dict(sorted(grouped.items(), reverse=True))

# -------------------------------
# MAIN API
# -------------------------------
@app.get("/")
def get_news():
    rss_data = fetch_rss_news()
    results = []

    for item in rss_data:
        title = item.get("title", "")

        if is_noise(title):
            continue

        country = detect_country(title)

        if country is None:
            if is_africa_related(title):
                country = "Regional"
            else:
                continue

        color = get_signal_color(title)
        source_type, weight = get_source_type(item.get("source", ""))

        results.append({
            "id": item.get("link", ""),  # 🔥 UNIQUE ID FOR FLUTTER
            "type": "rss",
            "country": country,
            "color": color,
            "source_type": source_type,
            "weight": weight,
            "title": title,
            "timestamp": item.get("published", ""),
            "source_url": item.get("link", "")
        })

    results = remove_duplicates(results)

    # SORT BY PRIORITY
    results.sort(key=lambda x: x["weight"], reverse=True)

    # TIMELINE OUTPUT
    return group_by_date(results)