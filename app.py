import difflib
import logging
from typing import List, Optional, Any
import pandas as pd
import streamlit as st
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import scipy.sparse

st.set_page_config(page_title="Hybrid Movie Recommender", page_icon="🎬", layout="wide")

DATA_FILE = "main_data.csv"


@st.cache_data(show_spinner=False)
def load_movies() -> pd.DataFrame:
    """
    Loads movie data from the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing movie data.

    Raises:
        ValueError: If required columns are missing.
    """
    try:
        movies_df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        st.error(f"❌ Could not find {DATA_FILE}. Please ensure the dataset exists.")
        st.stop()

    required_columns = {"comb", "movie_title"}
    missing_columns = required_columns - set(movies_df.columns)
    if missing_columns:
        st.error(
            f"❌ {DATA_FILE} is missing required columns: {sorted(missing_columns)}"
        )
        st.stop()
    movies_df["comb"] = movies_df["comb"].fillna("")
    return movies_df


@st.cache_resource(show_spinner=False)
def build_movie_vectors(movie_features: pd.Series) -> scipy.sparse.csr_matrix:
    """
    Builds a document-term matrix from movie features using CountVectorizer.

    Args:
        movie_features (pd.Series): A series containing text features for each movie.

    Returns:
        scipy.sparse.csr_matrix: The sparse matrix of token counts.
    """
    vectorizer = CountVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(movie_features)
    return matrix


def resolve_title(user_input: str, titles: List[str]) -> Optional[str]:
    """
    Resolves the user's input to the closest matching movie title.

    Args:
        user_input (str): The movie title inputted by the user.
        titles (List[str]): The list of valid movie titles to match against.

    Returns:
        Optional[str]: The closest matching title, or None if no match is found.
    """
    title_lookup = {title.lower(): title for title in titles}
    direct_match = title_lookup.get(user_input.strip().lower())
    if direct_match:
        return direct_match

    candidates = difflib.get_close_matches(
        user_input.strip().lower(), title_lookup.keys(), n=1, cutoff=0.6
    )
    if candidates:
        return title_lookup[candidates[0]]
    return None


def fetch_poster(movie_title: str, api_key: str) -> Optional[str]:
    """
    Fetches the poster URL for a given movie title from TMDB API.

    Args:
        movie_title (str): The title of the movie to fetch the poster for.
        api_key (str): The TMDB API key.

    Returns:
        Optional[str]: The URL of the poster image, or None if fetching fails.
    """
    if not api_key:
        return None
    url = "https://api.themoviedb.org/3/search/movie"
    try:
        response = requests.get(
            url, params={"api_key": api_key, "query": movie_title}, timeout=5
        )
        response.raise_for_status()
        data = response.json()
        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except Exception as e:
        logging.error(f"Error fetching poster for {movie_title}: {e}")
        # Fail for API errors so we still show local fallback
    return None


def get_recommendations(
    title: str,
    movies_df: pd.DataFrame,
    movie_matrix: scipy.sparse.csr_matrix,
    top_n: int = 10,
) -> List[pd.Series]:
    """
    Gets movie recommendations based on cosine similarity.

    Args:
        title (str): The title of the movie to base recommendations on.
        movies_df (pd.DataFrame): DataFrame containing movie data.
        movie_matrix (scipy.sparse.csr_matrix): Sparse matrix of movie features.
        top_n (int, optional): The number of recommendations to return. Defaults to 10.

    Returns:
        List[pd.Series]: A list of pandas Series objects representing recommended movies.
    """
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


# --- UI Layout ---

with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1485846234645-a62644f84728?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        use_container_width=True,
    )

    st.markdown("### 🌐 Live Global Engine Mode")
    st.info(
        "Unlock rich movie posters by providing your TMDB API Key. Without a key, the app runs locally."
    )
    default_api_key = os.environ.get("DEFAULT_TMDB_API_KEY", "")
    tmdb_api_key = st.text_input(
        "TMDB API Key",
        type="password",
        placeholder="Enter your key here",
        value=default_api_key,
    )
    st.write("---")

    st.title("About")
    st.info(
        "This project implements a movie recommendation system that uses hybrid filtering techniques "
        "to provide personalized movie recommendations to users. By combining content-based and "
        "collaborative filtering, it avoids common pitfalls like the cold start problem."
    )
    st.markdown("### Technologies Used")
    st.markdown("- Python\n- Streamlit\n- Scikit-learn\n- Pandas")
    st.markdown("### Author")
    st.markdown(
        "**Morris Darren Babu**\n\nM.S. Data Science, B.E. Computer Science\n\nFriedrich-Alexander-University Erlangen-Nürnberg"
    )

st.title("🎬 Ultimate Hybrid Movie Recommendation System")
st.markdown("##### *Discover your next favorite movie instantly.*")
st.write("---")

movies = load_movies()
movie_matrix = build_movie_vectors(movies["comb"])
titles = movies["movie_title"].dropna().tolist()

col1, col2 = st.columns([3, 1])
with col1:
    movie_input = st.selectbox(
        "Select a movie you love",
        options=titles,
        index=None,
        placeholder="e.g., Toy Story, Jumanji, The Matrix",
        help="Choose a movie, and we will find the best recommendations for you.",
    )
with col2:
    st.write("")  # spacing
    st.write("")
    recommend_button = st.button(
        "Get Recommendations", type="primary", use_container_width=True
    )

if recommend_button:
    if not movie_input.strip():
        st.warning("⚠️ Please enter a movie title to get started.")
    else:
        matched_title = resolve_title(movie_input, titles)
        if not matched_title:
            st.error("❌ Movie not found in our database. Please try another title.")
        else:
            with st.spinner("Finding the best movies for you..."):
                recommendations = get_recommendations(
                    matched_title, movies, movie_matrix
                )

            if not recommendations:
                st.error("❌ Could not generate recommendations for that title.")
            else:
                st.success(
                    f"✨ Top 10 recommendations based on **{matched_title.title()}**"
                )
                st.write("---")

                # Display recommendations in a grid
                cols = st.columns(5)
                for rank, row in enumerate(recommendations, start=1):
                    col_idx = (rank - 1) % 5
                    with cols[col_idx]:
                        movie_title = row["movie_title"].title()

                        poster_url = None
                        if tmdb_api_key:
                            poster_url = fetch_poster(movie_title, tmdb_api_key)

                        if poster_url:
                            st.image(poster_url, use_container_width=True)
                            st.markdown(f"**#{rank} {movie_title}**")
                        else:
                            st.markdown(
                                f"""
                                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; height: 250px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                    <h3 style="color: #1f77b4; font-size: 24px; margin-bottom: 5px;">#{rank}</h3>
                                    <h4 style="color: #333; font-size: 16px; margin: 0; line-height: 1.2;">{movie_title}</h4>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        # Optionally show genres if available
                        if "genres" in row and pd.notna(row["genres"]):
                            genres = str(row["genres"]).replace(" ", ", ")
                            st.caption(f"_{genres}_")
