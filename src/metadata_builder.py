import os
import ast
import pandas as pd
import numpy as np
import config

def parse_genres(genres_str):
    """Parse JSON string of genres and return a list of names."""
    try:
        genres_list = ast.literal_eval(genres_str)
        return [g["name"] for g in genres_list]
    except Exception:
        return []

def parse_cast(cast_str, top_n=5):
    """Parse JSON string of cast and return list of top N actor names."""
    try:
        cast_list = ast.literal_eval(cast_str)
        return [c["name"] for c in cast_list[:top_n]]
    except Exception:
        return []

def parse_director(crew_str):
    """Parse JSON string of crew and return director's name."""
    try:
        crew_list = ast.literal_eval(crew_str)
        for member in crew_list:
            if member.get("job") == "Director":
                return member.get("name", "")
        return ""
    except Exception:
        return ""

def build_metadata_cache(force=False):
    """Downloads TMDB dataset and compiles the metadata cache pickle if not present."""
    if config.METADATA_PKL.exists() and not force:
        try:
            # Validate shape alignment
            meta_df = pd.read_pickle(config.METADATA_PKL)
            movies_df = pd.read_pickle(config.MOVIES_PKL)
            if len(meta_df) == len(movies_df):
                print("Metadata cache already exists and matches movies index. Skipping build.")
                return True
            else:
                print(f"Metadata index size ({len(meta_df)}) mismatch with movies ({len(movies_df)}). Forcing rebuild...")
        except Exception:
            print("Failed to read metadata cache. Forcing rebuild...")


    print("Building metadata cache. This happens only once...")
    
    try:
        # Load existing movies dataframe to know which movies we need to align
        if not config.MOVIES_PKL.exists():
            raise FileNotFoundError(f"Original movies.pkl not found at {config.MOVIES_PKL}. Cannot build metadata.")
        
        movies_df = pd.read_pickle(config.MOVIES_PKL)
        target_ids = set(movies_df["id"].tolist())
        target_titles = set(movies_df["title"].tolist())

        # Download TMDB dataset from Kaggle
        import kagglehub
        print("Downloading TMDB dataset from Kagglehub...")
        dataset_path = kagglehub.dataset_download("tmdb/tmdb-movie-metadata")
        print(f"Dataset downloaded to: {dataset_path}")

        # Load CSVs
        movies_csv_path = os.path.join(dataset_path, "tmdb_5000_movies.csv")
        credits_csv_path = os.path.join(dataset_path, "tmdb_5000_credits.csv")

        if not os.path.exists(movies_csv_path) or not os.path.exists(credits_csv_path):
            raise FileNotFoundError("TMDB dataset files missing from download path.")

        print("Loading and merging CSVs...")
        raw_movies = pd.read_csv(movies_csv_path)
        raw_credits = pd.read_csv(credits_csv_path)

        # Merge on title (like the notebook did) or ID
        merged = raw_movies.merge(raw_credits, on="title")
        # Rename x and y IDs if they exist
        if "id_x" in merged.columns:
            merged["id"] = merged["id_x"]

        print("Cleaning and parsing columns...")
        # Parse fields
        merged["genres_list"] = merged["genres"].apply(parse_genres)
        merged["cast_list"] = merged["cast"].apply(parse_cast)
        merged["director"] = merged["crew"].apply(parse_director)
        
        # Release year
        merged["release_date"] = merged["release_date"].fillna("")
        merged["release_year"] = merged["release_date"].apply(
            lambda x: int(x.split("-")[0]) if x and len(x.split("-")) > 0 and x.split("-")[0].isdigit() else 0
        )
        
        # Rename/keep only required fields
        # Note: we also want to align it exactly with movies_df row count and index.
        # Let's clean the merged metadata
        metadata = merged[[
            "id", "title", "genres_list", "release_date", "release_year",
            "vote_average", "vote_count", "original_language", "overview",
            "runtime", "tagline", "cast_list", "director", "popularity"
        ]].copy()
        
        # Fill missing values
        metadata["overview"] = metadata["overview"].fillna("")
        metadata["tagline"] = metadata["tagline"].fillna("")
        metadata["runtime"] = metadata["runtime"].fillna(0)
        metadata["vote_average"] = metadata["vote_average"].fillna(0.0)
        metadata["vote_count"] = metadata["vote_count"].fillna(0)
        metadata["original_language"] = metadata["original_language"].fillna("en")

        # Ensure metadata has unique IDs before merging to avoid duplicate rows in the left join
        metadata = metadata.drop_duplicates(subset=["id"])

        # Merge alignment: we want to ensure we have metadata for ALL movies in movies_df
        # We perform a left merge from movies_df on 'id' to make sure
        # our metadata has the exact same row alignment and count as movies_df.
        print("Aligning metadata with movies.pkl...")
        
        # Standardize movies_df
        aligned_meta = pd.merge(movies_df[["id", "title"]], metadata, on="id", how="left", suffixes=("", "_meta"))

        
        # If any rows failed to join on ID, let's fallback to joining on Title
        missing_mask = aligned_meta["vote_average"].isna()
        if missing_mask.any():
            print(f"Resolving {missing_mask.sum()} missing items by title...")
            for idx, row in aligned_meta[missing_mask].iterrows():
                title = row["title"]
                matching_rows = metadata[metadata["title"] == title]
                if not matching_rows.empty:
                    match = matching_rows.iloc[0]
                    for col in metadata.columns:
                        if col != "id" and col != "title":
                            aligned_meta.at[idx, col] = match[col]
        
        # Fill any remaining NaNs with defaults
        aligned_meta["genres_list"] = aligned_meta["genres_list"].apply(lambda x: x if isinstance(x, list) else [])
        aligned_meta["cast_list"] = aligned_meta["cast_list"].apply(lambda x: x if isinstance(x, list) else [])
        aligned_meta["director"] = aligned_meta["director"].fillna("")
        aligned_meta["release_date"] = aligned_meta["release_date"].fillna("")
        aligned_meta["release_year"] = aligned_meta["release_year"].fillna(0).astype(int)
        aligned_meta["vote_average"] = aligned_meta["vote_average"].fillna(0.0)
        aligned_meta["vote_count"] = aligned_meta["vote_count"].fillna(0).astype(int)
        aligned_meta["original_language"] = aligned_meta["original_language"].fillna("en")
        aligned_meta["overview"] = aligned_meta["overview"].fillna("")
        aligned_meta["runtime"] = aligned_meta["runtime"].fillna(0).astype(int)
        aligned_meta["tagline"] = aligned_meta["tagline"].fillna("")
        aligned_meta["popularity"] = aligned_meta["popularity"].fillna(0.0)

        # Drop title_meta if created
        if "title_meta" in aligned_meta.columns:
            aligned_meta = aligned_meta.drop(columns=["title_meta"])

        # Save to pickle
        aligned_meta.to_pickle(config.METADATA_PKL)
        print(f"Successfully compiled and saved metadata to {config.METADATA_PKL} (Shape: {aligned_meta.shape})")
        return True

    except Exception as e:
        print(f"Error building metadata cache: {e}")
        # Build minimal fallback metadata from movies_df if possible
        try:
            print("Attempting to build minimal fallback metadata from movies.pkl...")
            movies_df = pd.read_pickle(config.MOVIES_PKL)
            fallback = pd.DataFrame({
                "id": movies_df["id"],
                "title": movies_df["title"],
                "genres_list": [[] for _ in range(len(movies_df))],
                "release_date": [""] * len(movies_df),
                "release_year": [0] * len(movies_df),
                "vote_average": [0.0] * len(movies_df),
                "vote_count": [0] * len(movies_df),
                "original_language": ["en"] * len(movies_df),
                "overview": ["No description available."] * len(movies_df),
                "runtime": [0] * len(movies_df),
                "tagline": [""] * len(movies_df),
                "cast_list": [[] for _ in range(len(movies_df))],
                "director": [""] * len(movies_df),
                "popularity": [0.0] * len(movies_df)
            })
            fallback.to_pickle(config.METADATA_PKL)
            print("Saved minimal fallback metadata.")
            return True
        except Exception as fallback_error:
            print(f"Critical error: Failed to save fallback metadata: {fallback_error}")
            return False

if __name__ == "__main__":
    build_metadata_cache(force=True)
