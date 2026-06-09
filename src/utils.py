import json
import streamlit as st
import config

def get_watchlist():
    """Loads watchlist from local json file."""
    if config.WATCHLIST_FILE.exists():
        try:
            with open(config.WATCHLIST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading watchlist: {e}")
    return []

def save_watchlist(watchlist):
    """Saves watchlist to local json file."""
    try:
        with open(config.WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(watchlist, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving watchlist: {e}")

def add_to_watchlist(movie_id, movie_title):
    """Adds a movie to the watchlist if not already present."""
    watchlist = get_watchlist()
    # Check if already exists
    if not any(item["id"] == int(movie_id) for item in watchlist):
        watchlist.append({
            "id": int(movie_id),
            "title": movie_title
        })
        save_watchlist(watchlist)
        return True
    return False

def remove_from_watchlist(movie_id):
    """Removes a movie from the watchlist by ID."""
    watchlist = get_watchlist()
    watchlist = [item for item in watchlist if item["id"] != int(movie_id)]
    save_watchlist(watchlist)

def in_watchlist(movie_id):
    """Checks if a movie is in the watchlist."""
    watchlist = get_watchlist()
    return any(item["id"] == int(movie_id) for item in watchlist)

def track_recently_viewed(movie_id, movie_title):
    """Adds a movie to the recently viewed queue in session state."""
    if "recently_viewed" not in st.session_state:
        st.session_state["recently_viewed"] = []
        
    recently_viewed = st.session_state["recently_viewed"]
    
    # Remove if already exists to move it to the front
    recently_viewed = [item for item in recently_viewed if item["id"] != int(movie_id)]
    
    # Add to the front
    recently_viewed.insert(0, {
        "id": int(movie_id),
        "title": movie_title
    })
    
    # Limit to top 10 items
    st.session_state["recently_viewed"] = recently_viewed[:10]

def track_recommendation_history(movie_title, recommendation_titles):
    """Tracks the history of recommendations requested."""
    if "recommendation_history" not in st.session_state:
        st.session_state["recommendation_history"] = []
        
    history = st.session_state["recommendation_history"]
    
    # Add to the front
    history.insert(0, {
        "movie_title": movie_title,
        "recommendations": recommendation_titles
    })
    
    st.session_state["recommendation_history"] = history[:10]

def generate_share_link(movie_title=None, ai_query=None):
    """Generates a shareable URL containing movie or AI query parameters."""
    # Attempt to retrieve hostname from headers
    # Note: Streamlit doesn't expose the base URL easily, so we use localhost default or dynamic port
    # In a real deployed app, it uses the host URL. We can construct a relative query path.
    # We will output a button that copies parameters to query params.
    if movie_title:
        return f"?movie={movie_title.replace(' ', '+')}"
    elif ai_query:
        return f"?ai_query={ai_query.replace(' ', '+')}"
    return ""
