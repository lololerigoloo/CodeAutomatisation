import os
from dotenv import load_dotenv
import requests
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

load_dotenv()

csv_lock = threading.Lock()
csv_file = "torrents.csv"

# Miroirs alternatifs à essayer dans l'ordre
APIBAY_MIRRORS = [
    "https://apibay.org/q.php",
    "https://piratebay.live/q.php",
    "https://thepiratebay.org/q.php",
    "https://tpb.party/q.php",
]

with open(csv_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Seeders", "Leechers", "Size", "Magnet", "Status"])

def fetch_torrents(query):
    """Essaie chaque miroir jusqu'à en trouver un qui répond."""
    for mirror in APIBAY_MIRRORS:
        try:
            response = requests.get(
                mirror,
                params={"q": query, "cat": "201"},
                timeout=8
            )
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            continue  # essaie le prochain miroir
    return None

def search_movie_or_series(query):
    torrents = fetch_torrents(query)

    if not torrents or torrents[0].get("id") == "0":
        print(f"Aucun résultat pour : {query}")
        return

    torrents.sort(key=lambda x: int(x.get("seeders", 0)), reverse=True)

    rows = []
    for t in torrents[:10]:
        size_mb = int(t["size"]) / (1024 * 1024)
        size_mb = f"{size_mb / 1024:.2f} GB" if size_mb > 1000 else f"{size_mb:.2f} MB"
        magnet = f"magnet:?xt=urn:btih:{t['info_hash']}&dn={requests.utils.quote(t['name'])}"
        rows.append([t['name'], t['seeders'], t['leechers'], size_mb, magnet, t['status']])

    with csv_lock:
        with open(csv_file, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    print(f"✓ {query}")

def get_popular_movies(nb_pages=1):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + os.getenv("API_KEY"),
    }
    tab = []
    for page in range(1, nb_pages + 1):
        print(f"Fetching page {page} of popular movies...")
        response = requests.get(
            "https://api.themoviedb.org/3/movie/top_rated",
            headers=headers,
            params={"page": page}
        )
        for movie in response.json().get("results", []):
            tab.append([movie['title'], movie['release_date'], movie['popularity']])
    return tab


tableau_titre = get_popular_movies(100)
titres = [titre for titre, date, popularite in tableau_titre]

with open("movie.txt", "w", encoding="utf-8") as f:
    for titre in titres:
        f.write(titre + "\n")
        