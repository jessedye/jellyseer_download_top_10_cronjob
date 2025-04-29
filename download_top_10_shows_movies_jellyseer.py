import os
import requests

# Configuration
JELLYSEERR_URL = "http://localhost:5055"
EMAIL = os.getenv("JELLYSEERR_EMAIL", "[YOUR_EMAIL]")
PASSWORD = os.getenv("JELLYSEERR_PASSWORD", "[YOUR_PASSWORD]")
OMDB_API_KEY = "[YOUR_API_KEY]"
MIN_IMDB_SCORE = 7.0
TARGET_LANGUAGE = "en"
EXCLUDED_GENRES = {99, 10767, 10763, 35, 10764}  # Documentary, Talk Show, News, Comedy, Reality
EXCLUDED_KEYWORDS = ["wrestling", "soap opera", "soap"]
MIN_YEAR = 2000
TOP_N = 10
MAX_PAGES = 300

# Logging and Request Control
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()  # "info" or "verbose"
ENABLE_REQUESTS = True  # Set to True to actually request media

session = requests.Session()

def log(message, level="info"):
    if level == "verbose" and LOG_LEVEL == "verbose":
        print(message)
    elif level == "info" and LOG_LEVEL in ["info", "verbose"]:
        print(message)

def login():
    res = session.post(f"{JELLYSEERR_URL}/api/v1/auth/local", json={"email": EMAIL, "password": PASSWORD})
    if res.status_code == 200:
        log("✅ Logged in to Jellyseerr", "info")
        return True
    log(f"❌ Login failed: {res.text}", "info")
    return False

def get_imdb_rating(title, year):
    params = {"apikey": OMDB_API_KEY, "t": title, "y": year}
    try:
        res = requests.get("https://www.omdbapi.com/", params=params)
        log(f"\n🔍 Requesting OMDb for: {title} ({year})", "verbose")
        log(f"📡 URL: {res.url}", "verbose")
        data = res.json()
        log(f"📄 Response: {data}", "verbose")
        if data.get("Response") == "True":
            return float(data.get("imdbRating")) if data.get("imdbRating") != "N/A" else None
    except Exception as e:
        log(f"❌ Error querying OMDb: {e}", "verbose")
    return None

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
        log(f"📥 Requested: {title}", "info")
    else:
        log(f"❌ Failed to request {title}: {res.status_code} {res.text}", "info")

def should_include(media, media_type):
    release_date = media.get("releaseDate") or media.get("firstAirDate") or "0000"
    try:
        year = int(release_date[:4])
    except ValueError:
        year = 0

    title = media.get("title") if media_type == "movies" else media.get("name")

    if year < MIN_YEAR:
        log(f"❌ Excluded due to year ({year}): {title}", "verbose")
        return False

    if media.get("originalLanguage") != TARGET_LANGUAGE:
        log(f"❌ Excluded due to language ({media.get('originalLanguage')}): {title}", "verbose")
        return False

    media_genres = set(media.get("genreIds", []))
    if EXCLUDED_GENRES & media_genres:
        log(f"❌ Excluded due to genres: {title}", "verbose")
        return False

    description = media.get("overview", "").lower()
    if any(keyword in description for keyword in EXCLUDED_KEYWORDS):
        log(f"❌ Excluded due to keywords in description: {title}", "verbose")
        return False

    imdb_rating = get_imdb_rating(title, year)
    if imdb_rating is None or imdb_rating < MIN_IMDB_SCORE:
        log(f"❌ Excluded due to IMDb rating ({imdb_rating}): {title}", "verbose")
        return False

    media["imdb_rating"] = imdb_rating
    return True

def get_top_media(media_type):
    top_media = []
    page = 1

    while len(top_media) < TOP_N and page <= MAX_PAGES:
        res = session.get(f"{JELLYSEERR_URL}/api/v1/discover/{media_type}?page={page}")
        if res.status_code != 200:
            log(f"❌ Failed to fetch {media_type}: {res.text}", "info")
            break

        media_list = res.json().get("results", [])
        log(f"📄 Fetching page {page} for {media_type}: {len(media_list)} items", "info")

        for media in media_list:
            if should_include(media, media_type):
                top_media.append(media)
                title = media.get("title") if media_type == "movies" else media.get("name")
                log(f"✅ Included: {title} ({media.get('releaseDate') or media.get('firstAirDate')}) [IMDb {media['imdb_rating']}]", "info")
                if ENABLE_REQUESTS:
                    request_media(media)

        page += 1

    return top_media[:TOP_N]

def main():
    if not login():
        return

    top_shows = get_top_media("tv")
    top_movies = get_top_media("movies")

    log(f"\n🎯 Final TV Shows fetched: {len(top_shows)}", "info")
    log(f"🎯 Final Movies fetched: {len(top_movies)}", "info")

if __name__ == "__main__":
    main()

