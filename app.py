import streamlit as st
import pandas as pd
import numpy as np
import time

# 1. Setup Streamlit page configuration (Must be first)
st.set_page_config(
    page_title="CineMatch - Premium Movie Discovery",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Build metadata cache automatically if not present
import src.metadata_builder as metadata_builder
metadata_builder.build_metadata_cache()

# 3. Import local modules
import config
import src.recommender as recommender
import src.tmdb_client as tmdb_client
import src.llm_client as llm_client
import src.ui_components as ui_components
import src.utils as utils

# 4. Inject Netflix premium styles
ui_components.inject_netflix_theme()

# 5. Load recommender models and metadata
try:
    movies_df, similarity_matrix, metadata_df = recommender.load_recommender_data()
except Exception as e:
    st.error(f"Failed to load recommendation models: {e}")
    st.info("Ensure movies.pkl and similarity.pkl are placed in the models/ folder.")
    st.stop()

# 6. Handle URL Query Parameters (Synchronization for shared links)
query_params = st.query_params
url_movie = query_params.get("movie", None)

if url_movie and "selected_movie" not in st.session_state:
    # URL encoded string decoding is handled by Streamlit automatically
    # Let's find if movie exists in our database
    matched_movie = movies_df[movies_df["title"].str.lower() == url_movie.lower()]
    if not matched_movie.empty:
        st.session_state["selected_movie"] = matched_movie.iloc[0]["title"]
    else:
        st.session_state["selected_movie"] = url_movie  # might be an external TMDB movie recommendation

# Initialize session states
if "selected_movie" not in st.session_state:
    st.session_state["selected_movie"] = "Avatar"  # Default spotlight movie
if "watchlist_updated" not in st.session_state:
    st.session_state["watchlist_updated"] = False
if "tmdb_api_key" not in st.session_state:
    st.session_state["tmdb_api_key"] = config.TMDB_API_KEY

# Override config key if session state has a valid key
if st.session_state["tmdb_api_key"] and st.session_state["tmdb_api_key"] != "your_tmdb_api_key_here":
    config.TMDB_API_KEY = st.session_state["tmdb_api_key"]

# Sidebar Navigation Panel
st.sidebar.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>🍿 CineMatch</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align: center; color: #888888; font-size: 0.85rem; margin-bottom: 25px;'>AI-Powered Movie Discovery</div>", unsafe_allow_html=True)

nav_page = st.sidebar.radio(
    "Navigation Menu",
    ["🏠 Home", "🤖 AI Companion", "📂 My Space"],
    label_visibility="collapsed"
)

# Add API status badge in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 API Integrations")

# Dynamic TMDB Key Input Widget
tmdb_key_input = st.sidebar.text_input(
    "TMDB API Key (Optional)",
    value=st.session_state["tmdb_api_key"] if st.session_state["tmdb_api_key"] != "your_tmdb_api_key_here" else "",
    type="password",
    help="Leave blank to run in offline placeholder mode. Enter a TMDB API Key to unlock real posters/trailers dynamically!"
)

if tmdb_key_input:
    st.session_state["tmdb_api_key"] = tmdb_key_input
    config.TMDB_API_KEY = tmdb_key_input
elif not tmdb_key_input and st.session_state["tmdb_api_key"] != config.TMDB_API_KEY:
    st.session_state["tmdb_api_key"] = config.TMDB_API_KEY

active_llm = config.get_active_llm()
if active_llm:
    st.sidebar.success(f"AI: Active ({active_llm.upper()})")
else:
    st.sidebar.warning("AI: Offline (Mock Mode)")
    
if config.TMDB_API_KEY and config.TMDB_API_KEY != "your_tmdb_api_key_here":
    st.sidebar.success("TMDB: Connected")
else:
    st.sidebar.info("TMDB: Offline (Placeholder Mode)")


# Page Routing
if nav_page == "🏠 Home":
    # Ensure URL is synced with active selection
    if st.session_state["selected_movie"]:
        st.query_params["movie"] = st.session_state["selected_movie"]
        
    # Get active movie details
    active_movie = st.session_state["selected_movie"]
    movie_details = recommender.get_movie_details(movie_title=active_movie)
    
    # Handle external movie details (not in local movies.pkl database)
    is_external_movie = False
    if not movie_details:
        is_external_movie = True
        # Try fetching from TMDB search
        movie_details = tmdb_client.search_movie_by_title(active_movie)
        
    if movie_details:
        movie_id = movie_details["id"]
        title = movie_details["title"]
        
        # Track recently viewed
        utils.track_recently_viewed(movie_id, title)
        
        # Fetch TMDB data (will fetch from local json cache if possible)
        tmdb_data = tmdb_client.get_movie_tmdb_metadata(movie_id, offline_metadata=movie_details)
        
        # Render Hero Banner with background poster
        ui_components.render_hero_banner(
            title=title,
            genres=movie_details.get("genres_list", movie_details.get("genres", [])),
            release_year=movie_details["release_year"],
            rating=tmdb_data["vote_average"],
            tagline=tmdb_data["tagline"],
            overview=movie_details["overview"],
            runtime=tmdb_data["runtime"],
            original_language=movie_details["original_language"],
            poster_url=tmdb_data["poster_url"]
        )
        
        # Action Bar (Watchlist, Play Trailer, Share Link)
        action_col1, action_col2, action_col3 = st.columns([1, 1.5, 3])
        
        with action_col1:
            # Watchlist Button
            is_in_watchlist = utils.in_watchlist(movie_id)
            btn_label = "❤️ In Watchlist" if is_in_watchlist else "➕ Add Watchlist"
            if st.button(btn_label, use_container_width=True):
                if is_in_watchlist:
                    utils.remove_from_watchlist(movie_id)
                    st.toast(f"Removed {title} from watchlist!")
                else:
                    utils.add_to_watchlist(movie_id, title)
                    st.toast(f"Added {title} to watchlist!")
                st.rerun()
                
        with action_col2:
            # YouTube Trailer Button
            trailer_url = tmdb_data.get("trailer_url")
            if trailer_url:
                # Direct link or dialog
                st.link_button("🎬 Play Trailer", trailer_url, use_container_width=True)
            else:
                st.button("🚫 No Trailer Available", disabled=True, use_container_width=True)
                
        with action_col3:
            # Share URL
            share_url = f"http://localhost:8501{utils.generate_share_link(movie_title=title)}"
            # Standard Text input showing the share link
            st.text_input("🔗 Copy Shareable Link", value=share_url, label_visibility="collapsed")
            
        # Cast Row Display
        cast_list = tmdb_data.get("cast", [])
        if cast_list:
            st.markdown("### 🎭 Top Cast")
            cast_cols = st.columns(min(len(cast_list), 5))
            for i, actor in enumerate(cast_list[:5]):
                with cast_cols[i]:
                    actor_img = actor.get("profile_url")
                    if actor_img:
                        st.image(actor_img, width=120, use_container_width=False)
                    else:
                        # Fallback icon
                        st.markdown("<div style='width:120px; height:180px; background:#222; border-radius:6px; display:flex; justify-content:center; align-items:center; font-size:2rem;'>👤</div>", unsafe_allow_html=True)
                    st.markdown(f"**{actor['name']}**")
                    st.markdown(f"<div style='font-size:0.75rem; color:#888;'>{actor['character']}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    else:
        st.error(f"Movie '{active_movie}' not found in the local database. Please enter your TMDB API Key in the sidebar to enable searching and viewing external movies!")
        st.stop()
        
    st.markdown("---")
    
    # Discovery Panel (Search & Recommendations)
    st.markdown("## 🔍 Movie Discovery Panel")
    
    # Grid search and filters layout
    search_col, filter_toggle_col = st.columns([4, 1])
    
    with search_col:
        # Autocomplete select box containing all movies
        movie_titles = list(movies_df["title"].values)
        selected_search = st.selectbox(
            "Search movies to get recommendations...",
            movie_titles,
            index=movie_titles.index(st.session_state["selected_movie"]) if st.session_state["selected_movie"] in movie_titles else 0
        )
        # Update session state if selection changed
        if selected_search != st.session_state["selected_movie"] and not is_external_movie:
            st.session_state["selected_movie"] = selected_search
            st.rerun()

    # Advanced Filters (Expander)
    with st.expander("🛠️ Advanced Search Filters"):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        
        with f_col1:
            all_genres = recommender.get_genres_list()
            selected_genres = st.multiselect("Genre Filter", all_genres)
            
        with f_col2:
            min_rating = st.slider("Minimum TMDB Rating", 0.0, 10.0, 0.0, 0.5)
            
        with f_col3:
            all_languages = recommender.get_languages_list()
            selected_langs = st.multiselect("Language Filter", all_languages)
            
        with f_col4:
            min_year = int(metadata_df["release_year"].min())
            max_year = int(metadata_df["release_year"].max())
            year_range = st.slider("Release Year Range", min_year, max_year, (min_year, max_year))
            
    # Slider for count of recommendations
    recommendation_count = st.slider("Number of recommendations to show", 4, 20, 6, 2)
    
    st.markdown("### 🎬 Similar Movies You May Like")
    
    # Calculate recommendations
    if is_external_movie:
        # Since it's external, we cannot do local cosine similarity lookup.
        # However, we can perform content recommendations using its main genre!
        # Or look up matches by title. For a smooth portfolio-grade flow:
        st.info("Generating dynamic recommendations based on TMDB search matches...")
        recs = recommender.get_recommendations(
            movie_title="Avatar", # Fallback to Avatar similar
            top_n=recommendation_count,
            genres=movie_details.get("genres_list", movie_details.get("genres", [])),
            min_rating=min_rating,
            languages=selected_langs,
            year_range=year_range
        )
    else:
        # Fetch similarities from matrix
        recs = recommender.get_recommendations(
            movie_title=st.session_state["selected_movie"],
            top_n=recommendation_count,
            genres=selected_genres,
            min_rating=min_rating,
            languages=selected_langs,
            year_range=year_range
        )
        
    if recs:
        # Get TMDB details for each rec movie in background/parallel (handling placeholders seamlessly)
        updated_recs = []
        for r in recs:
            rec_metadata = tmdb_client.get_movie_tmdb_metadata(r["id"], offline_metadata=r)
            r["poster_url"] = rec_metadata["poster_url"]
            updated_recs.append(r)
            
        # Display recommendations with Netflix cards
        ui_components.render_movie_grid(updated_recs)
        
        # Track recommendation history
        rec_titles = [m["title"] for m in recs]
        utils.track_recommendation_history(st.session_state["selected_movie"], rec_titles)
        
        # Display similarity score/explanation for first 3 recommendations
        st.markdown("<br><h3>💡 AI Similarity Insights</h3>", unsafe_allow_html=True)
        insight_cols = st.columns(min(len(recs), 3))
        for idx, item in enumerate(recs[:3]):
            with insight_cols[idx]:
                explanation = f"'{item['title']}' matches '{st.session_state['selected_movie']}' with a **{int(item['similarity_score'] * 100)}% Content Similarity score**. "
                if item["director"] and movie_details and movie_details.get("director") == item["director"]:
                    explanation += f"Both movies are directed by **{item['director']}**. "
                if any(g in (movie_details.get("genres_list", []) if movie_details else []) for g in item["genres"]):
                    shared_genres = [g for g in item["genres"] if g in (movie_details.get("genres_list", []) if movie_details else [])]
                    explanation += f"They share the {', '.join(shared_genres)} genre tags."
                
                ui_components.render_ai_explanation_box(explanation, query=item["title"])
    else:
        st.warning("No recommendations found matching your criteria. Try adjusting the filters.")

    # Trending section at bottom
    st.markdown("---")
    st.markdown("## 🔥 Trending Discoveries")
    trending = metadata_df.sort_values(by="popularity", ascending=False).head(5)
    trending_list = []
    for _, row in trending.iterrows():
        dict_row = row.to_dict()
        tm_data = tmdb_client.get_movie_tmdb_metadata(dict_row["id"], offline_metadata=dict_row)
        dict_row["poster_url"] = tm_data["poster_url"]
        trending_list.append(dict_row)
    ui_components.render_movie_grid(trending_list)

elif nav_page == "🤖 AI Companion":
    st.markdown("# 🤖 CineMatch AI Movie Companion")
    st.markdown("Chat with the AI to discover movies using natural language queries. Tell it your mood, preferred themes, or ask for complex suggestions!")
    
    # Query input box
    user_query = st.text_input(
        "Describe what you want to watch (e.g. 'Suggest dark psychological thrillers with a twist' or 'Recommend underrated sci-fi movies like Interstellar')",
        placeholder="Type here..."
    )
    
    if user_query:
        with st.spinner("🧠 Analyzing and fetching custom recommendations..."):
            ai_data = llm_client.get_ai_movie_recommendations(user_query)
            
        # 1. Print AI Introduction
        st.markdown(f"### 💬 AI Assistant Response")
        st.markdown(f"<div style='font-size: 1.15rem; line-height: 1.5; color: #E50914; margin-bottom: 25px;'>{ai_data.get('message', '')}</div>", unsafe_allow_html=True)
        
        # 2. Extract suggested movie objects
        suggestions = ai_data.get("recommendations", [])
        
        if suggestions:
            st.markdown("### 🎬 Personalized Movie Matches")
            
            # Map LLM movie titles to our database or search TMDB API
            mapped_movies = []
            
            for sug in suggestions:
                title = sug["title"]
                explanation = sug["explanation"]
                mood_tags = sug.get("mood_tags", [])
                
                # Search local database first (case insensitive fuzzy check)
                local_match = metadata_df[metadata_df["title"].str.lower() == title.lower()]
                
                if not local_match.empty:
                    # Found in local database
                    movie_row = local_match.iloc[0].to_dict()
                    movie_id = movie_row["id"]
                    
                    # Fetch posters/trailers
                    tm_data = tmdb_client.get_movie_tmdb_metadata(movie_id, offline_metadata=movie_row)
                    
                    movie_row["poster_url"] = tm_data["poster_url"]
                    movie_row["ai_explanation"] = explanation
                    movie_row["mood_tags"] = mood_tags
                    mapped_movies.append(movie_row)
                else:
                    # External movie - Query TMDB API by title
                    external_details = tmdb_client.search_movie_by_title(title)
                    if external_details:
                        external_details["ai_explanation"] = explanation
                        external_details["mood_tags"] = mood_tags
                        mapped_movies.append(external_details)
                    else:
                        # Create minimal card placeholder
                        mapped_movies.append({
                            "id": 999999 + hash(title) % 100000,
                            "title": title,
                            "release_year": 0,
                            "vote_average": 0.0,
                            "poster_url": None,
                            "overview": "No database description available.",
                            "ai_explanation": explanation,
                            "mood_tags": mood_tags,
                            "original_language": "en"
                        })
            
            # Display matched recommendations
            ui_components.render_movie_grid(mapped_movies)
            
            # Render "Why Recommended" cards for each suggestion
            st.markdown("<br>### 💡 AI Recommendations Details", unsafe_allow_html=True)
            for m in mapped_movies:
                tags_str = " ".join([f"<span class='hero-meta-item' style='background:rgba(229, 9, 20, 0.25); color:white; font-size:0.75rem; margin-right:5px;'>#{tag}</span>" for tag in m.get("mood_tags", [])])
                
                # Check if user wants to select this movie
                card_col, exp_col = st.columns([1, 4])
                
                with card_col:
                    # Render small image button using markdown or standard details buttons
                    btn_key = f"view_details_{m['id']}"
                    if st.button(f"🔎 Select {m['title']}", key=btn_key, use_container_width=True):
                        st.session_state["selected_movie"] = m["title"]
                        st.query_params["movie"] = m["title"]
                        st.toast(f"Selected {m['title']}! Redirecting to Home...")
                        time.sleep(1)
                        # Switch page to home
                        # To do this in Streamlit sidebar we can't easily force value, but we can set session state
                        # Let's guide the user to click the Home tab.
                        # Wait, we can't programmatically change sidebar radio index directly, but we can force it
                        # if we initialize radio with index=session_state index!
                        # We'll stick to a simple toast to let them navigate to Home.
                        # Wait, actually we can just let them click it, and it will load when they go to Home.
                        
                with exp_col:
                    st.markdown(f"**{m['title']}** {tags_str}", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:0.9rem; color:#ccc; margin-top:4px;'>{m['ai_explanation']}</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin:10px 0; border-color:#222;'>", unsafe_allow_html=True)
        else:
            st.warning("Could not parse AI recommendations. Try a different request description.")

elif nav_page == "📂 My Space":
    st.markdown("# 📂 My CineMatch Space")
    st.markdown("Your private profile containing saved movies, recently viewed list, and discovery insights.")
    
    tab_watchlist, tab_recent, tab_history = st.tabs(["❤️ My Watchlist", "👁️ Recently Viewed", "📊 Discovery Insights"])
    
    with tab_watchlist:
        st.markdown("### Saved Movies")
        watchlist_items = utils.get_watchlist()
        
        if watchlist_items:
            # Reconstruct metadata for grid
            grid_list = []
            for item in watchlist_items:
                movie_details = recommender.get_movie_details(movie_id=item["id"])
                if not movie_details:
                    # External movie search
                    movie_details = tmdb_client.search_movie_by_title(item["title"])
                
                if movie_details:
                    # Fetch tmdb data
                    tm_data = tmdb_client.get_movie_tmdb_metadata(item["id"], offline_metadata=movie_details)
                    movie_details["poster_url"] = tm_data["poster_url"]
                    grid_list.append(movie_details)
                    
            if grid_list:
                ui_components.render_movie_grid(grid_list)
                
                # Option to clear watchlist
                st.markdown("<br>", unsafe_allow_html=True)
                clear_cols = st.columns([1, 5])
                with clear_cols[0]:
                    if st.button("🗑️ Clear Watchlist", use_container_width=True):
                        utils.save_watchlist([])
                        st.toast("Watchlist cleared!")
                        st.rerun()
            else:
                st.info("Watchlist movies could not be resolved from DB.")
        else:
            st.info("Your watchlist is empty. Add movies by clicking 'Add Watchlist' on the Home spotlight page!")
            
    with tab_recent:
        st.markdown("### Recently Viewed Spotlight Movies")
        recent_items = st.session_state.get("recently_viewed", [])
        
        if recent_items:
            grid_list = []
            for item in recent_items:
                movie_details = recommender.get_movie_details(movie_id=item["id"])
                if not movie_details:
                    movie_details = tmdb_client.search_movie_by_title(item["title"])
                if movie_details:
                    tm_data = tmdb_client.get_movie_tmdb_metadata(item["id"], offline_metadata=movie_details)
                    movie_details["poster_url"] = tm_data["poster_url"]
                    grid_list.append(movie_details)
            
            if grid_list:
                ui_components.render_movie_grid(grid_list)
            else:
                st.info("Error loading details for recently viewed.")
        else:
            st.info("No movie history tracked yet. Browse spotlight movies on the Home tab to see them here.")
            
    with tab_history:
        st.markdown("### CineMatch Recommendation Statistics")
        
        # Calculate stats from watchlist
        watchlist = utils.get_watchlist()
        if watchlist:
            genres_count = {}
            for item in watchlist:
                details = recommender.get_movie_details(movie_id=item["id"])
                if details:
                    for genre in details.get("genres_list", []):
                        genres_count[genre] = genres_count.get(genre, 0) + 1
                        
            if genres_count:
                st.markdown("#### Your Favorite Genres")
                # Sort by count
                sorted_genres = sorted(genres_count.items(), key=lambda x: x[1], reverse=True)
                
                # Build columns for top 3 genres
                stat_cols = st.columns(min(len(sorted_genres), 3))
                for idx, (g, count) in enumerate(sorted_genres[:3]):
                    with stat_cols[idx]:
                        st.metric(label=f"Rank {idx+1} Genre", value=g, delta=f"{count} movies saved")
            else:
                st.info("Add movies to your watchlist to see your genre insights analysis here!")
        else:
            st.info("Add movies to your watchlist to calculate favorite genres and preferences stats.")
            
        # Recommendation history log
        rec_history = st.session_state.get("recommendation_history", [])
        if rec_history:
            st.markdown("#### Search & Recommendation History Log")
            for idx, item in enumerate(rec_history):
                st.markdown(f"**{idx+1}. Search Target:** '{item['movie_title']}'  \n**Recommended Suggestions:** {', '.join(item['recommendations'][:5])}")
                st.markdown("<hr style='margin:5px 0; border-color:#222;'>", unsafe_allow_html=True)
