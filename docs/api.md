# API & Extensibility

The core application (`app.py`) exposes several isolated functions that can be imported and reused in larger systems.

### `load_movies() -> pd.DataFrame`
Loads and validates the core dataset.
*   **Behavior**: Caches the result in memory using `@st.cache_data`. Stops the application safely if the file or required columns are missing.

### `build_movie_vectors(movie_features: pd.Series) -> scipy.sparse.csr_matrix`
The core NLP pipeline.
*   **Arguments**: A Pandas Series of strings (the `comb` column).
*   **Returns**: A highly compressed sparse matrix containing token counts, removing english stop-words.

### `resolve_title(user_input: str, titles: List[str]) -> Optional[str]`
Robust fuzzy matching.
*   **Behavior**: Attempts a direct exact match first (case-insensitive). If it fails, falls back to `difflib.get_close_matches` with a 0.6 cutoff.

### `fetch_poster(movie_title: str, api_key: str) -> Optional[str]`
The external integration point.
*   **Behavior**: Queries the TMDB `search/movie` endpoint. Gracefully fails and returns `None` on timeouts or HTTP errors, ensuring the app continues to function in "Local Mode".
