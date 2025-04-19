import requests
import os
import time

# Configuration
JELLYSEERR_URL = "http://localhost:5055"
EMAIL = os.getenv("JELLYSEERR_EMAIL", "ENTER_YOUR_EMAIL_HERE")
PASSWORD = os.getenv("JELLYSEERR_PASSWORD", "ENTER_YOUR_PASSWORD")
LANGUAGE = "en"

# Session setup
session = requests.Session()

def login():
    login_url = f"{JELLYSEERR_URL}/api/v1/auth/local"
    res = session.post(login_url, json={"email": EMAIL, "password": PASSWORD})
    if res.status_code == 200:
        print("✅ Logged in to Jellyseerr")
        return True
    print(f"❌ Login failed: {res.status_code} {res.text}")
    return False

def get_trending():
    url = f"{JELLYSEERR_URL}/api/v1/discover/trending"
    res = session.get(url)
    if res.status_code == 200:
        all_results = res.json().get("results", [])
        filtered = [item for item in all_results if item.get("originalLanguage") == LANGUAGE]
        return filtered
    print(f"❌ Failed to fetch trending: {res.status_code} {res.text}")
    return []

def request_media(media_type, media_id, title):
    payload = {
        "mediaType": media_type,
        "mediaId": media_id
    }
    if media_type == "tv":
        payload["seasons"] = "all"

    res = session.post(f"{JELLYSEERR_URL}/api/v1/request", json=payload)
    if res.status_code in [200, 201]:
        print(f"✅ Requested: {title}")
    else:
        print(f"❌ Failed to request {title}: {res.status_code} {res.text}")

def main():
    if not login():
        return

    trending = get_trending()
    if not trending:
        return

    movies = [item for item in trending if item.get("mediaType") == "movie"][:10]
    shows = [item for item in trending if item.get("mediaType") == "tv"][:10]

    print("\n🎬 Top 10 Trending Movies:")
    for item in movies:
        title = item.get("title", "Untitled")
        media_id = item.get("id")
        print(f"\n▶️ Requesting: {title}")
        request_media("movie", media_id, title)
        time.sleep(1)

    print("\n📺 Top 10 Trending TV Shows:")
    for item in shows:
        title = item.get("name", "Untitled")
        media_id = item.get("id")
        print(f"\n▶️ Requesting: {title}")
        request_media("tv", media_id, title)
        time.sleep(1)

if __name__ == "__main__":
    main()
