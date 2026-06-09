import pandas as pd
import numpy as np
import streamlit as st
import config

@st.cache_resource
def load_recommender_data():
    """Loads and caches the movie models and metadata."""
    if not config.MOVIES_PKL.exists() or not config.SIMILARITY_PKL.exists():
        raise FileNotFoundError("Core model files movies.pkl or similarity.pkl are missing from models/ folder.")
    
    # Load movies list
    movies_df = pd.read_pickle(config.MOVIES_PKL)
    
    # Load similarity matrix
    similarity_matrix = pd.read_pickle(config.SIMILARITY_PKL)
    
    # Load rich metadata
    if config.METADATA_PKL.exists():
        metadata_df = pd.read_pickle(config.METADATA_PKL)
    else:
        # Fallback to loading minimal version if metadata isn't compiled yet
        metadata_df = pd.DataFrame({
            "id": movies_df["id"],
            "title": movies_df["title"],
            "genres_list": [[] for _ in range(len(movies_df))],
            "release_date": [""] * len(movies_df),
            "release_year": [0] * len(movies_df),
            "vote_average": [0.0] * len(movies_df),
            "vote_count": [0] * len(movies_df),
            "original_language": ["en"] * len(movies_df),
            "overview": [""] * len(movies_df),
            "runtime": [0] * len(movies_df),
            "tagline": [""] * len(movies_df),
            "cast_list": [[] for _ in range(len(movies_df))],
            "director": [""] * len(movies_df),
            "popularity": [0.0] * len(movies_df)
        })

    return movies_df, similarity_matrix, metadata_df

def get_genres_list():
    """Returns a sorted list of all unique genres in the dataset."""
    _, _, metadata_df = load_recommender_data()
    genres = set()
    for row in metadata_df["genres_list"]:
        if isinstance(row, list):
            genres.update(row)
    return sorted(list(genres))

def get_languages_list():
    """Returns a sorted list of all unique original languages in the dataset."""
    _, _, metadata_df = load_recommender_data()
    languages = metadata_df["original_language"].dropna().unique().tolist()
    return sorted(list(set(languages)))

def get_movie_details(movie_id=None, movie_title=None):
    """Retrieves metadata details for a specific movie by ID or title."""
    _, _, metadata_df = load_recommender_data()
    
    if movie_id is not None:
        match = metadata_df[metadata_df["id"] == int(movie_id)]
    elif movie_title is not None:
        match = metadata_df[metadata_df["title"] == movie_title]
    else:
        return None
        
    if not match.empty:
        return match.iloc[0].to_dict()
    return None

def get_recommendations(movie_title, top_n=5, genres=None, min_rating=0.0, languages=None, year_range=None):
    """
    Finds and ranks movies similar to the target movie, applying specified metadata filters.
    
    Args:
        movie_title (str): Title of the reference movie.
        top_n (int): Number of recommendations to return.
        genres (list): List of genres to filter by (movie must match AT LEAST one).
        min_rating (float): Minimum TMDB rating.
        languages (list): List of languages to filter by.
        year_range (tuple): (min_year, max_year) filter.
        
    Returns:
        list of dicts: Recommendations with titles, ids, metadata, and similarity scores.
    """
    movies_df, similarity_matrix, metadata_df = load_recommender_data()
    
    # Check if movie exists
    matches = movies_df[movies_df["title"] == movie_title]
    if matches.empty:
        return []
        
    movie_index = matches.index[0]
    
    # Get similarity distances
    distances = similarity_matrix[movie_index]
    
    # Create a copy of metadata_df to filter and compute scores
    df_scores = metadata_df.copy()
    df_scores["similarity_score"] = distances
    
    # Exclude the search movie itself
    df_scores = df_scores[df_scores["title"] != movie_title]
    
    # Apply filters
    # 1. Genre filter (any matching genre)
    if genres:
        # Check if list of genres intersects with genres_list
        df_scores = df_scores[df_scores["genres_list"].apply(lambda x: any(g in x for g in genres))]
        
    # 2. Rating filter
    if min_rating > 0.0:
        df_scores = df_scores[df_scores["vote_average"] >= min_rating]
        
    # 3. Language filter
    if languages:
        df_scores = df_scores[df_scores["original_language"].isin(languages)]
        
    # 4. Year range filter
    if year_range:
        min_yr, max_yr = year_range
        df_scores = df_scores[(df_scores["release_year"] >= min_yr) & (df_scores["release_year"] <= max_yr)]
        
    # Sort by similarity score descending
    recommendations_df = df_scores.sort_values(by="similarity_score", ascending=False).head(top_n)
    
    results = []
    for _, row in recommendations_df.iterrows():
        results.append({
            "id": int(row["id"]),
            "title": row["title"],
            "genres": row["genres_list"],
            "release_year": int(row["release_year"]),
            "release_date": row["release_date"],
            "vote_average": float(row["vote_average"]),
            "vote_count": int(row["vote_count"]),
            "original_language": row["original_language"],
            "overview": row["overview"],
            "runtime": int(row["runtime"]),
            "tagline": row["tagline"],
            "cast": row["cast_list"],
            "director": row["director"],
            "similarity_score": round(float(row["similarity_score"]), 3)
        })
        
    return results
