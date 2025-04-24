import os
import requests
import time

# Configuration
JELLYSEERR_URL = "http://localhost:5055"
EMAIL = os.getenv("JELLYSEERR_EMAIL", "[YOUR_EMAIL]")
PASSWORD = os.getenv("JELLYSEERR_PASSWORD", "[YOUR_PASSWORD]")
OMDB_API_KEY = "[OMDB_API_KEY]"
MIN_IMDB_SCORE = 6.0
TARGET_LANGUAGE = "en"
EXCLUDED_GENRES = {99, 10767}  # Documentary and Talk Show

session = requests.Session()

def login():
    res = session.post(f"{JELLYSEERR_URL}/api/v1/auth/local", json={"email": EMAIL, "password": PASSWORD})
    if res.status_code == 200:
        print("✅ Logged in to Jellyseerr")
        return True
    print(f"❌ Login failed: {res.status_code} {res.text}")
    return False

def get_imdb_rating(title, year):
    params = {"apikey": OMDB_API_KEY, "t": title, "y": year}
    try:
        res = requests.get("https://www.omdbapi.com/", params=params)
        print(f"\n🔍 Requesting OMDb for: {title} ({year})")
        print(f"📡 URL: {res.url}")
        data = res.json()
        print(f"📄 Response: {data}")
        if data.get("Response") == "True":
            return float(data.get("imdbRating")) if data.get("imdbRating") != "N/A" else None
    except Exception as e:
        print(f"❌ Error querying OMDb: {e}")
    return None

def should_include(media):
    title = media.get("title") or media.get("name")
    year = media.get("releaseDate", media.get("firstAirDate", "0"))[:4]

    if media.get("originalLanguage") != TARGET_LANGUAGE:
        print(f"🌐 Skipping {title} (Non-English: {media.get('originalLanguage')})")
        return False

    if any(genre_id in EXCLUDED_GENRES for genre_id in media.get("genreIds", [])):
        print(f"🎭 Skipping {title} (Excluded Genre: {media.get('genreIds')})")
        return False

    print(f"🎯 Checking media: {title} ({year})")
    imdb_score = get_imdb_rating(title, year)
    if imdb_score is None:
        print(f"❌ Skipping {title} (IMDb None)")
        return False

    if imdb_score >= MIN_IMDB_SCORE:
        print(f"✅ Accepted {title} (IMDb {imdb_score})")
        return True

    print(f"❌ Skipping {title} (IMDb {imdb_score} < {MIN_IMDB_SCORE})")
    return False

def fetch_trending(page):
    url = f"{JELLYSEERR_URL}/api/v1/discover/trending?page={page}"
    res = session.get(url)
    if res.status_code != 200:
        print(f"⚠️ Failed to fetch trending: {res.status_code}")
        return []
    return res.json().get("results", [])

def request_media(media):
    payload = {
        "mediaType": media["mediaType"],
        "mediaId": media["id"]
    }
    if media["mediaType"] == "tv":
        payload["seasons"] = "all"

    res = session.post(f"{JELLYSEERR_URL}/api/v1/request", json=payload)
    title = media.get("title") or media.get("name")
    if res.status_code in [200, 201]:
        print(f"📥 Requested: {title}")
    else:
        print(f"❌ Failed to request {title}: {res.status_code} {res.text}")

def main():
    if not login():
        return

    top_movies, top_shows = [], []
    page = 1
    while (len(top_movies) < 20 or len(top_shows) < 20) and page <= 25:
        results = fetch_trending(page)
        if not results:
            break

        for media in results:
            if len(top_movies) >= 20 and len(top_shows) >= 20:
                break

            if not should_include(media):
                continue

            if media["mediaType"] == "movie" and len(top_movies) < 20:
                top_movies.append(media)
                request_media(media)

            elif media["mediaType"] == "tv" and len(top_shows) < 20:
                top_shows.append(media)
                request_media(media)

        page += 1
        time.sleep(0.5)

    print(f"\n🎬 Top Movies Collected: {len(top_movies)}")
    print(f"📺 Top Shows Collected: {len(top_shows)}")

if __name__ == "__main__":
    main()
