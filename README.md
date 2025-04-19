# 🎬 Jellyseerr Auto Requester

This Python script automatically logs into your [Jellyseerr](https://github.com/fallenbagel/jellyseerr) server and requests the top 10 trending **movies** and **TV shows** using the built-in `/discover/trending` API endpoint.

---

## 📦 Features

- ✅ Authenticates with your Jellyseerr account
- 🔥 Fetches top 10 trending movies and shows
- 💬 Set your Language Preference
- 📡 Sends media requests automatically via Jellyseerr API
- 🔒 No TMDB API key required (uses Jellyseerr's own metadata)

---

## 🚀 Usage

1. **Clone the repo or download the script**

2. **Set environment variables** (recommended):

```bash
export JELLYSEERR_URL="http://localhost:5055"
export JELLYSEERR_EMAIL="you@example.com"
export JELLYSEERR_PASSWORD="yourpassword"
export LANGUAGE="en"
```

3. **Run the script**:

```bash
python3 download_top_10.py
```

Notes
The script uses the Jellyseerr /discover/trending endpoint.

Items that are already requested or downloaded may still be attempted depending on your Jellyseerr settings.

Jellyseerr must be running and accessible at the provided URL.

Requirements
Python 3.6+

requests library

Install with:

```bash
pip install requests
```

License
MIT License. Use at your own risk. Not affiliated with Jellyseerr or TMDB.

