# Getting Started

This guide will help you understand how to use the Hybrid Movie Recommendation System out of the box.

## User Experience

1.  **Launch the App**: When you open the application, you are presented with a clean interface.
2.  **Global Engine vs Local Mode**:
    *   **Local Mode**: Runs entirely on the pre-processed `main_data.csv`. Fast, private, but lacks rich media (like posters).
    *   **Global Engine Mode**: By providing a TMDB API key in the sidebar (or via the `DEFAULT_TMDB_API_KEY` environment variable), the app fetches high-quality movie posters dynamically.
3.  **Search**: Use the dropdown to select a movie you enjoy. The system uses fuzzy matching, so minor typos are handled gracefully.
4.  **Recommendations**: Click "Get Recommendations". The Scikit-Learn engine calculates the cosine similarity and returns the top 10 closest matches instantly.
