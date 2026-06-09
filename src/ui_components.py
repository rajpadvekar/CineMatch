import streamlit as st

def inject_netflix_theme():
    """Injects custom CSS to override Streamlit styling and apply a premium Netflix-inspired dark theme."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    /* Global settings */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0c0c0c !important;
        color: #ffffff !important;
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* Header background transparent */
    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0) !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #121212 !important;
        border-right: 1px solid #222222;
        box-shadow: 4px 0px 20px rgba(0,0,0,0.8);
    }
    
    [data-testid="stSidebar"] .stMarkdown h1, 
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #E50914 !important;
        font-weight: 800;
        letter-spacing: 0.5px;
    }

    /* Customize standard inputs and selects */
    div[data-baseweb="select"] {
        background-color: #222222 !important;
        border-radius: 6px !important;
        border: 1px solid #333333 !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: transparent !important;
        color: #ffffff !important;
    }

    input[type="text"] {
        background-color: #222222 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 6px !important;
    }
    
    /* Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #E50914 0%, #B20710 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 0.5rem 1.8rem !important;
        box-shadow: 0 4px 15px rgba(229, 9, 20, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(229, 9, 20, 0.5) !important;
        color: #ffffff !important;
    }

    /* Secondary outline button style for details */
    div.detail-btn-container button {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        box-shadow: none !important;
    }
    
    div.detail-btn-container button:hover {
        background: rgba(255,255,255,0.2) !important;
        border-color: rgba(255,255,255,0.4) !important;
    }
    
    /* Movie Card Styles */
    .movie-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 24px;
        padding: 16px 0;
    }
    
    .movie-card {
        background-color: #181818;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        text-decoration: none !important;
        color: inherit !important;
        border: 1px solid #222222;
        display: flex;
        flex-direction: column;
        height: 100%;
        position: relative;
    }
    
    .movie-card:hover {
        transform: translateY(-8px) scale(1.03);
        border-color: #E50914;
        box-shadow: 0 12px 30px rgba(229, 9, 20, 0.25);
    }
    
    .movie-poster-container {
        position: relative;
        width: 100%;
        padding-top: 150%; /* 2:3 Aspect Ratio */
        background-color: #252525;
    }
    
    .movie-poster-img {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    /* Poster gradient placeholder */
    .poster-placeholder {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #1f1f1f 0%, #111111 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 20px;
        text-align: center;
        box-sizing: border-box;
    }
    
    .poster-placeholder-icon {
        font-size: 3rem;
        color: #E50914;
        margin-bottom: 12px;
    }
    
    .poster-placeholder-title {
        font-weight: 800;
        font-size: 1.1rem;
        color: #ffffff;
        margin: 0;
        line-height: 1.2;
    }
    
    .movie-info {
        padding: 12px 14px;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
        justify-content: space-between;
    }
    
    .movie-title {
        font-size: 1rem;
        font-weight: 600;
        color: #ffffff;
        margin: 0 0 6px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .movie-meta-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.8rem;
        color: #b3b3b3;
    }
    
    .movie-rating {
        color: #ffb400;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 3px;
    }
    
    .similarity-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(229, 9, 20, 0.9);
        color: white;
        padding: 3px 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,0,0,0.5);
        z-index: 10;
    }
    
    /* Hero Banner styles */
    .hero-banner {
        background: linear-gradient(to right, rgba(0,0,0,0.95) 40%, rgba(0,0,0,0.2) 100%), var(--hero-bg);
        background-size: cover;
        background-position: center;
        border-radius: 12px;
        padding: 40px 50px;
        margin-bottom: 35px;
        min-height: 380px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid #222222;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    }
    
    .hero-pretitle {
        color: #E50914;
        font-size: 0.85rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 8px;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: white;
        margin: 0 0 12px 0;
        line-height: 1.1;
    }
    
    .hero-meta {
        display: flex;
        gap: 16px;
        align-items: center;
        font-size: 0.9rem;
        color: #cccccc;
        margin-bottom: 16px;
    }
    
    .hero-meta-item {
        background: rgba(255,255,255,0.1);
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    
    .hero-rating {
        color: #ffb400;
        font-weight: 800;
    }
    
    .hero-tagline {
        font-style: italic;
        color: #aaaaaa;
        margin-bottom: 12px;
        font-size: 1.1rem;
    }
    
    .hero-overview {
        max-width: 600px;
        color: #e5e5e5;
        line-height: 1.5;
        margin-bottom: 20px;
        font-size: 0.95rem;
    }
    
    /* AI Explanation card */
    .ai-explanation-box {
        background: linear-gradient(135deg, rgba(229, 9, 20, 0.08) 0%, rgba(18, 18, 18, 0.8) 100%);
        border-left: 4px solid #E50914;
        border-radius: 0 8px 8px 0;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .ai-explanation-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #E50914;
        margin: 0 0 6px 0;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .ai-explanation-text {
        font-size: 0.9rem;
        color: #dddddd;
        margin: 0;
        line-height: 1.4;
    }
    
    /* Tab Container overriding */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #222222;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent !important;
        border: none !important;
        color: #808080 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 3px solid #E50914 !important;
    }
    
    /* Skeleton Loader */
    .skeleton-card {
        background: #181818;
        border-radius: 8px;
        height: 350px;
        position: relative;
        overflow: hidden;
        border: 1px solid #222222;
    }
    
    .skeleton-card::after {
        content: "";
        display: block;
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        animation: loading 1.5s infinite;
    }
    
    @keyframes loading {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_hero_banner(title, genres, release_year, rating, tagline, overview, runtime, original_language, poster_url=None):
    """Renders a Netflix-style Hero Banner for the active selected movie."""
    # Set default backdrops
    bg_style = ""
    if poster_url:
        bg_style = f"style='--hero-bg: url({poster_url});'"
    else:
        bg_style = "style='--hero-bg: linear-gradient(135deg, #220204 0%, #0d0d0d 100%);'"
        
    genres_str = ", ".join(genres) if genres else "Unknown Genre"
    tagline_html = f"<div class='hero-tagline'>\"{tagline}\"</div>" if tagline else ""
    lang_code = original_language.upper() if original_language else "EN"
    
    html = (
        f"<div class='hero-banner' {bg_style}>"
        f"<div class='hero-pretitle'>Featured Spotlight</div>"
        f"<h1 class='hero-title'>{title}</h1>"
        f"<div class='hero-meta'>"
        f"<span class='hero-rating'>★ {rating:.1f}</span>"
        f"<span class='hero-meta-item'>{release_year}</span>"
        f"<span class='hero-meta-item'>{runtime} min</span>"
        f"<span class='hero-meta-item'>{lang_code}</span>"
        f"</div>"
        f"<div style='color: #b3b3b3; font-size: 0.85rem; font-weight:600; margin-bottom: 12px;'>{genres_str}</div>"
        f"{tagline_html}"
        f"<p class='hero-overview'>{overview}</p>"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)

def draw_movie_card_html(title, poster_url, rating, year, similarity_score=None):
    """Generates the HTML string representing a single movie card with hover styles."""
    similarity_badge = ""
    if similarity_score is not None:
        similarity_badge = f"<div class='similarity-badge'>{int(similarity_score * 100)}% Match</div>"
        
    # Safe encoding of title for URL query parameter
    safe_title = title.replace(" ", "+")
    href_link = f"?movie={safe_title}"
    
    if poster_url:
        poster_content = f"<img class='movie-poster-img' src='{poster_url}' alt='{title}' loading='lazy'>"
    else:
        # Initial letters of the movie
        initials = "".join([w[0] for w in title.split()[:2]]).upper()
        poster_content = (
            f"<div class='poster-placeholder'>"
            f"<div class='poster-placeholder-icon'>🎬</div>"
            f"<p class='poster-placeholder-title'>{title}</p>"
            f"<div style='font-size: 2.2rem; font-weight: 800; color: rgba(255,255,255,0.06); margin-top: 15px;'>{initials}</div>"
            f"</div>"
        )
        
    html = (
        f"<a class='movie-card' href='{href_link}' target='_self'>"
        f"{similarity_badge}"
        f"<div class='movie-poster-container'>{poster_content}</div>"
        f"<div class='movie-info'>"
        f"<h3 class='movie-title' title='{title}'>{title}</h3>"
        f"<div class='movie-meta-row'>"
        f"<span class='movie-rating'>★ {rating:.1f}</span>"
        f"<span>{year}</span>"
        f"</div>"
        f"</div>"
        f"</a>"
    )
    return html

def render_movie_grid(movies_list):
    """Renders a grid of Netflix styled cards in Streamlit."""
    grid_html = "<div class='movie-grid'>"
    for m in movies_list:
        grid_html += draw_movie_card_html(
            title=m["title"],
            poster_url=m.get("poster_url"),
            rating=m["vote_average"],
            year=m["release_year"],
            similarity_score=m.get("similarity_score")
        )
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

def render_ai_explanation_box(explanation, query=None):
    """Renders a stylized highlight card representing explanation from AI model."""
    prefix = f"🤖 CineMatch AI Companion"
    if query:
         prefix += f" (re: '{query}')"
    html = (
        f"<div class='ai-explanation-box'>"
        f"<h4 class='ai-explanation-title'>💡 Why recommended:</h4>"
        f"<p class='ai-explanation-text'>{explanation}</p>"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)

def render_skeleton_loaders(count=4):
    """Renders a grid of loading skeleton placeholders."""
    cols = st.columns(count)
    for i in range(count):
        with cols[i]:
            st.markdown("<div class='skeleton-card'></div>", unsafe_allow_html=True)
