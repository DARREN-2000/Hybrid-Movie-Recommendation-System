# System Architecture

The recommendation engine is built to be modular, fast, and capable of running entirely in-browser.

## Data Flow
![Data Flow](diagrams/data_flow.mermaid)

1.  **Ingestion**: `main_data.csv` is loaded into a Pandas DataFrame.
2.  **Vectorization**: The `comb` text feature is transformed by `sklearn.feature_extraction.text.CountVectorizer`. This creates a sparse matrix where each row represents a movie and each column represents a token.
3.  **Matching**: User input is matched against known titles using `difflib` to ensure exact indexing.
4.  **Similarity**: `sklearn.metrics.pairwise.cosine_similarity` calculates the angle between the target movie's vector and all other vectors. The highest scores (closest to 1) represent the best recommendations.

## Edge Compute (Stlite)
By utilizing `@stlite/mountable` via `index.html`, this Python application is compiled to WebAssembly (Pyodide). This means the Scikit-Learn logic, the Pandas dataframe manipulation, and the Streamlit UI rendering all happen within the user's browser, enabling free deployment on static hosts like GitHub Pages.
