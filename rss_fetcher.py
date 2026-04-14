import feedparser

def fetch_rss_news():
    urls = [
        # AFRICA CORE
        "http://feeds.bbci.co.uk/news/world/africa/rss.xml",

        # GLOBAL MEDIA (filtered later)
        "https://www.aljazeera.com/xml/rss/all.xml",
        "http://rss.cnn.com/rss/edition.rss",
        "https://feeds.reuters.com/reuters/worldNews",
        "https://feeds.reuters.com/reuters/businessNews",
        "https://feeds.reuters.com/reuters/politicsNews",

        # GOVERNMENT / OFFICIAL
        "https://www.gov.za/rss.xml",        # South Africa Govt
        "https://www.cbn.gov.ng/rssfeed.asp" # Nigeria Central Bank
    ]

    all_articles = []

    for url in urls:
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:10]:
                article = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "source": url,

                    # 🔥 TIMESTAMP (CRITICAL FOR TIMELINE)
                    "published": entry.get("published", "") or entry.get("updated", "")
                }

                # Skip empty titles (important safety)
                if not article["title"]:
                    continue

                all_articles.append(article)

        except Exception as e:
            print(f"Error fetching {url}: {e}")

    return all_articles


# -------------------------------
# TEST RUN
# -------------------------------
if __name__ == "__main__":
    news = fetch_rss_news()

    print(f"\nTotal articles fetched: {len(news)}\n")

    for n in news:
        print(n)