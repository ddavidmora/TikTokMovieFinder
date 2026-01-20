import os
import requests
from dotenv import load_dotenv

load_dotenv()
TMDB_TOKEN = os.getenv("TMDB_API_KEY")


def search_tmdb(movie_title):
    """
    Searches TMDB for a movie and returns the top result's details.
    """
    if not movie_title:
        return None

    # TMDB Search Endpoint
    url = f"https://api.themoviedb.org/3/search/movie?query={movie_title}&include_adult=false&language=en-US&page=1"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        # If we found results, grab the first one (Ground Truth)
        if data.get("results"):
            top_match = data["results"][0]
            return {
                "id": top_match["id"],
                "title": top_match["title"],
                "year": top_match.get("release_date", "N/A").split("-")[0],
                "overview": top_match.get("overview", "No plot available."),
                "poster_url": f"https://image.tmdb.org/t/p/w500{top_match.get('poster_path')}",
                "rating": top_match.get("vote_average", "N/A")
            }
        else:
            return None

    except Exception as e:
        print(f"❌ Error connecting to TMDB: {e}")
        return None