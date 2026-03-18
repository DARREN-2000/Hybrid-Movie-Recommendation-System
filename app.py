import difflib

import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
        recommendations.append(movies_df.iloc[movie_idx]["movie_title"])
    return recommendations


st.set_page_config(page_title="Hybrid Movie Recommender Demo", page_icon="🎬")
st.title("🎬 Hybrid Movie Recommendation Demo")
st.write("Type any movie title and get 10 similar recommendations.")

movies = load_movies()
movie_matrix = build_movie_vectors(movies["comb"])
titles = movies["movie_title"].dropna().tolist()

movie_input = st.text_input("Movie title", placeholder="e.g., toy story")

if st.button("Recommend", type="primary"):
    if not movie_input.strip():
        st.warning("Please enter a movie title.")
    else:
        matched_title = resolve_title(movie_input, titles)
        if not matched_title:
            st.error("Movie not found. Try a different title.")
        else:
            recommendations = get_recommendations(matched_title, movies, movie_matrix)
            if not recommendations:
                st.error("Could not generate recommendations for that title.")
            else:
                st.success(f"Showing recommendations for: {matched_title}")
                for rank, recommendation in enumerate(recommendations, start=1):
                    st.write(f"{rank}. {recommendation}")
