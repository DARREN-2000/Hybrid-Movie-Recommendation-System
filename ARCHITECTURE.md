# Architecture

The Hybrid Movie Recommendation System is built on a streamlined, fast, and local-first architecture designed to operate seamlessly both in standard server environments and directly within the browser using WebAssembly.

## High-Level Overview

The system consists of three main tiers:
1.  **Data Tier**: A local, curated CSV dataset containing pre-processed IMDB movie metadata, optionally supplemented by the live TMDB API for rich media (posters).
2.  **Processing Engine**: A Scikit-Learn-powered machine learning engine that normalizes features, builds sparse vector representations, and calculates cosine similarity in real-time.
3.  **Application Tier**: A Streamlit application that handles the user interface, routing, and interactions. This layer can optionally be deployed via `stlite` to run entirely client-side.

## Detailed Component Responsibilities

### `app.py`
The core application file. It acts as both the controller and the view:
*   **Data Loading**: Uses `st.cache_data` to efficiently load and hold `main_data.csv` in memory.
*   **Vectorization**: Uses `st.cache_resource` to instantiate a `CountVectorizer`, which transforms the combined text features (`comb` column) into a SciPy Compressed Sparse Row (CSR) matrix.
*   **Recommendation Logic**: Computes the dot product (cosine similarity) between the queried movie vector and all other movie vectors in the space to find the top $N$ closest matches.
*   **Fuzzy Matching**: Employs `difflib.get_close_matches` to provide robust, typo-tolerant input handling for movie titles.
*   **UI Rendering**: Constructs the Streamlit interface, managing sidebar configurations, input fields, and the responsive grid layout for recommendations.

### `index.html` (Stlite Deployment)
Enables edge deployment without a traditional backend server.
*   Uses `@stlite/mountable` to create a virtual Python environment in the browser via Pyodide (WebAssembly).
*   Mounts `app.py` and `main_data.csv` directly into the client's memory.

### Data Model (`main_data.csv`)
*   Contains core features such as `movie_title` and `comb`.
*   The `comb` column represents a pre-computed string of relevant tags (genres, actors, directors) designed specifically for optimized CountVectorizer parsing.

## Extension Points
The architecture is designed to be easily extensible:
*   **Alternative Models**: The CSR matrix approach can be seamlessly replaced with embeddings (e.g., Word2Vec, BERT) by modifying the `build_movie_vectors` function.
*   **External Data**: The `fetch_poster` utility can be expanded to fetch trailers, cast lists, or real-time ratings.
