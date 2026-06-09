import json
import requests
import config

def load_cache():
    """Loads the TMDB metadata cache from disk."""
    if config.TMDB_CACHE_FILE.exists():
        try:
            with open(config.TMDB_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading TMDB cache: {e}")
    return {}

def save_cache(cache):
    """Saves the TMDB metadata cache to disk."""
    try:
        with open(config.TMDB_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving TMDB cache: {e}")

# Global cache reference
_tmdb_cache = load_cache()

def get_movie_tmdb_metadata(movie_id, offline_metadata=None):
    """
    Fetches rich movie details (poster, trailer, cast) from TMDB or cache.
    Falls back to offline metadata if TMDB fails or key is missing.
    
    Args:
        movie_id (int): The TMDB movie ID.
        offline_metadata (dict, optional): Fallback dictionary with metadata from models/movie_metadata.pkl.
        
    Returns:
        dict: Keys include 'poster_url', 'trailer_url', 'cast', and 'tagline'.
    """
    movie_id_str = str(movie_id)
    
    # 1. Return from cache if present
    if movie_id_str in _tmdb_cache:
        return _tmdb_cache[movie_id_str]
        
    # Default fallback values
    fallback_data = {
        "poster_url": None,
        "trailer_url": None,
        "cast": offline_metadata.get("cast", []) if offline_metadata else [],
        "tagline": offline_metadata.get("tagline", "") if offline_metadata else "",
        "vote_average": offline_metadata.get("vote_average", 0.0) if offline_metadata else 0.0,
        "runtime": offline_metadata.get("runtime", 0) if offline_metadata else 0
    }
    
    # If no TMDB API key is available, return fallback immediately
    if not config.TMDB_API_KEY or config.TMDB_API_KEY == "your_tmdb_api_key_here":
        return fallback_data
        
    try:
        # Base url for request
        base_api_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"api_key": config.TMDB_API_KEY}
        
        # 2. Fetch movie details (poster path, runtime, tagline)
        details_response = requests.get(base_api_url, params=params, timeout=5)
        
        if details_response.status_code == 200:
            details = details_response.json()
            poster_path = details.get("poster_path")
            poster_url = f"{config.TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None
            tagline = details.get("tagline", "")
            vote_average = details.get("vote_average", 0.0)
            runtime = details.get("runtime", 0)
        else:
            poster_url = None
            tagline = ""
            vote_average = 0.0
            runtime = 0
            
        # 3. Fetch video details (Youtube trailers)
        video_response = requests.get(f"{base_api_url}/videos", params=params, timeout=5)
        trailer_url = None
        if video_response.status_code == 200:
            videos = video_response.json().get("results", [])
            # Search for YouTube trailer
            for vid in videos:
                if vid.get("site") == "YouTube" and vid.get("type") == "Trailer":
                    trailer_url = f"https://www.youtube.com/watch?v={vid.get('key')}"
                    break
                    
        # 4. Fetch cast credits details
        credits_response = requests.get(f"{base_api_url}/credits", params=params, timeout=5)
        cast = []
        if credits_response.status_code == 200:
            cast_list = credits_response.json().get("cast", [])
            # Get top 5 actors with names and characters
            for actor in cast_list[:5]:
                profile_path = actor.get("profile_path")
                cast.append({
                    "name": actor.get("name"),
                    "character": actor.get("character"),
                    "profile_url": f"{config.TMDB_IMAGE_BASE_URL}{profile_path}" if profile_path else None
                })
        else:
            # Parse from offline_metadata
            cast = [{"name": name, "character": "Actor", "profile_url": None} for name in (offline_metadata.get("cast", []) if offline_metadata else [])]
            
        # Compile final details
        cached_result = {
            "poster_url": poster_url,
            "trailer_url": trailer_url,
            "cast": cast,
            "tagline": tagline,
            "vote_average": vote_average,
            "runtime": runtime
        }
        
        # 5. Write to global cache and disk
        _tmdb_cache[movie_id_str] = cached_result
        save_cache(_tmdb_cache)
        
        return cached_result
        
    except Exception as e:
        print(f"Error fetching TMDB API for movie {movie_id}: {e}")
        return fallback_data


def search_movie_by_title(title):
    """
    Searches for a movie by title using TMDB API.
    Returns basic details if found (id, title, poster_url, overview, release_year, vote_average, etc.).
    """
    if not config.TMDB_API_KEY or config.TMDB_API_KEY == "your_tmdb_api_key_here":
        return None
        
    # Standardize/clean title
    title = title.strip()
    if not title:
        return None
        
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": config.TMDB_API_KEY,
            "query": title,
            "language": "en-US",
            "page": 1,
            "include_adult": False
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                movie = results[0]
                poster_path = movie.get("poster_path")
                poster_url = f"{config.TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None
                
                release_date = movie.get("release_date", "")
                release_year = int(release_date.split("-")[0]) if release_date else 0
                
                movie_id = int(movie.get("id"))
                
                # Fetch full details (cast and trailer) via cache-supported fetcher
                extra = get_movie_tmdb_metadata(movie_id)
                
                return {
                    "id": movie_id,
                    "title": movie.get("title"),
                    "poster_url": poster_url,
                    "overview": movie.get("overview", ""),
                    "release_year": release_year,
                    "vote_average": float(movie.get("vote_average", 0.0)),
                    "tagline": extra.get("tagline", ""),
                    "trailer_url": extra.get("trailer_url"),
                    "cast": extra.get("cast", []),
                    "runtime": int(extra.get("runtime", 0))
                }
        return None
    except Exception as e:
        print(f"Error searching TMDB by title '{title}': {e}")
        return None

