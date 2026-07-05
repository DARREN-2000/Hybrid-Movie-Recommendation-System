# Installation

Running the system locally is straightforward and requires only a standard Python environment.

## Prerequisites
*   Python 3.9+
*   Git

## Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/DARREN-2000/Hybrid-Movie-Recommendation-System.git
    cd Hybrid-Movie-Recommendation-System
    ```

2.  **Create a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables (Optional):**
    To enable TMDB posters without entering a key in the UI, export:
    ```bash
    export DEFAULT_TMDB_API_KEY="your_tmdb_api_key_here"
    ```

5.  **Run the Application:**
    ```bash
    streamlit run app.py
    ```
    The application will be available at `http://localhost:8501`.
