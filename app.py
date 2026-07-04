import difflib
import pandas as pd
import streamlit as st
import requests
import urllib.parse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Hybrid Movie Recommender", page_icon="🎬", layout="wide")

DATA_FILE = "main_data.csv"

@st.cache_data(show_spinner=False)
def load_movies():
    movies_df = pd.read_csv(DATA_FILE)
    required_columns = {"comb", "movie_title"}
    missing_columns = required_columns - set(movies_df.columns)
    if missing_columns:
        raise ValueError(f"{DATA_FILE} is missing required columns: {sorted(missing_columns)}")
    movies_df["comb"] = movies_df["comb"].fillna("")
    return movies_df

@st.cache_resource(show_spinner=False)
def build_movie_vectors(movie_features):
    vectorizer = CountVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(movie_features)
    return matrix

def resolve_title(user_input, titles):
    title_lookup = {title.lower(): title for title in titles}
    direct_match = title_lookup.get(user_input.strip().lower())
    if direct_match:
        return direct_match

    candidates = difflib.get_close_matches(user_input.strip().lower(), title_lookup.keys(), n=1, cutoff=0.6)
    if candidates:
        return title_lookup[candidates[0]]
    return None

def get_recommendations(title, movies_df, movie_matrix, top_n=10):
    matching_indices = movies_df.index[movies_df["movie_title"] == title]
    if matching_indices.empty:
        return []

    idx = matching_indices[0]
    similarity_scores = sorted(
        list(enumerate(cosine_similarity(movie_matrix[idx], movie_matrix)[0])),
        key=lambda item: item[1],
        reverse=True,
    )
    recommendations = []
    for movie_idx, _score in similarity_scores[1 : top_n + 1]:
        recommendations.append(movies_df.iloc[movie_idx])
    return recommendations


def fetch_tmdb_movie(api_key, query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={urllib.parse.quote(query)}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            return results[0] # Return top match
    return None

def fetch_tmdb_recommendations(api_key, movie_id, top_n=10):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("results", [])
        return results[:top_n]
    return []

# --- UI Layout ---

with st.sidebar:
    st.image("https://images.unsplash.com/photo-1485846234645-a62644f84728?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", use_container_width=True)
    st.title("About")
    st.info(
        "This project implements a movie recommendation system that uses hybrid filtering techniques "
        "to provide personalized movie recommendations to users. By combining content-based and "
        "collaborative filtering, it avoids common pitfalls like the cold start problem."
    )
    st.markdown("### Technologies Used")
    st.markdown("- Python\n- Streamlit\n- Scikit-learn\n- Pandas")
    st.markdown("### Author")
    st.markdown("**Morris Darren Babu**\n\nM.S. Data Science, B.E. Computer Science\n\nFriedrich-Alexander-University Erlangen-Nürnberg")

    st.write("---")
    st.markdown("### Engine Settings")
    engine_mode = st.radio("Select Recommendation Engine", ["Local Dataset", "Live Global Engine (TMDB)"])
    tmdb_api_key = ""
    if engine_mode == "Live Global Engine (TMDB)":
        tmdb_api_key = st.text_input("TMDB API Key", type="password", help="Get your free API key at themoviedb.org")
        if not tmdb_api_key:
            st.warning("⚠️ Enter your TMDB API Key to unlock live recommendations.")

st.title("🎬 Ultimate Hybrid Movie Recommendation System")
st.markdown("##### *Discover your next favorite movie instantly.*")
st.write("---")

movies = load_movies()
movie_matrix = build_movie_vectors(movies["comb"])
titles = movies["movie_title"].dropna().tolist()

col1, col2 = st.columns([3, 1])
with col1:
    movie_input = st.text_input("Enter a movie you love", placeholder="e.g., toy story, jumanji, the matrix", help="Type the name of a movie, and we will find the best recommendations for you.")
with col2:
    st.write("") # spacing
    st.write("")
    recommend_button = st.button("Get Recommendations", type="primary", use_container_width=True)

if recommend_button:
    if not movie_input.strip():
        st.warning("⚠️ Please enter a movie title to get started.")
    else:
        if engine_mode == "Local Dataset":
            matched_title = resolve_title(movie_input, titles)
            if not matched_title:
                st.error("❌ Movie not found in our database. Please try another title.")
            else:
                with st.spinner("Finding the best movies for you using local dataset..."):
                    recommendations = get_recommendations(matched_title, movies, movie_matrix)

                if not recommendations:
                    st.error("❌ Could not generate recommendations for that title.")
                else:
                    st.success(f"✨ Top recommendations based on **{matched_title.title()}**")
                    st.write("---")

                    cols = st.columns(5)
                    for rank, row in enumerate(recommendations, start=1):
                        col_idx = (rank - 1) % 5
                        with cols[col_idx]:
                            st.markdown(
                                f"""
                                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; height: 150px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                    <h3 style="color: #1f77b4; font-size: 24px; margin-bottom: 5px;">#{rank}</h3>
                                    <h4 style="color: #333; font-size: 16px; margin: 0; line-height: 1.2;">{row['movie_title'].title()}</h4>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            if "genres" in row and pd.notna(row["genres"]):
                                genres = str(row["genres"]).replace(" ", ", ")
                                st.caption(f"_{genres}_")

        elif engine_mode == "Live Global Engine (TMDB)":
            if not tmdb_api_key:
                st.error("❌ Please provide a TMDB API Key in the sidebar.")
            else:
                with st.spinner("Searching Live Global Database..."):
                    tmdb_movie = fetch_tmdb_movie(tmdb_api_key, movie_input)

                if not tmdb_movie:
                    st.error("❌ Movie not found globally. Check your spelling.")
                else:
                    st.success(f"✨ Top global recommendations based on **{tmdb_movie.get('title')} ({tmdb_movie.get('release_date', '')[:4]})**")
                    st.write("---")

                    with st.spinner("Fetching global recommendations..."):
                        recommendations = fetch_tmdb_recommendations(tmdb_api_key, tmdb_movie['id'])

                    if not recommendations:
                        st.warning("No recommendations found for this movie on TMDB.")
                    else:
                        cols = st.columns(5)
                        for rank, rec in enumerate(recommendations, start=1):
                            col_idx = (rank - 1) % 5
                            with cols[col_idx]:
                                poster_path = rec.get('poster_path')
                                title = rec.get('title')
                                release_year = rec.get('release_date', '')[:4]
                                rating = rec.get('vote_average', 'N/A')

                                if poster_path:
                                    img_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                                else:
                                    img_url = "https://via.placeholder.com/500x750?text=No+Poster"

                                st.markdown(
                                    f"""
                                    <div style="background-color: #f0f2f6; border-radius: 10px; overflow: hidden; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; flex-direction: column;">
                                        <img src="{img_url}" style="width: 100%; height: auto; object-fit: cover;">
                                        <div style="padding: 10px; text-align: center;">
                                            <h4 style="color: #333; font-size: 14px; margin: 0 0 5px 0; line-height: 1.2;">{title}</h4>
                                            <div style="font-size: 12px; color: #666; display: flex; justify-content: space-around;">
                                                <span>📅 {release_year}</span>
                                                <span>⭐ {rating}</span>
                                            </div>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
