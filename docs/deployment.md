# Deployment

Because the application supports WebAssembly via `stlite`, deployment is incredibly flexible.

## Option 1: Streamlit Community Cloud (Recommended)
This is the standard deployment method for Streamlit apps.
1. Connect your GitHub repository to [share.streamlit.io](https://share.streamlit.io).
2. Set `app.py` as the entry point.
3. In the advanced settings, set the `DEFAULT_TMDB_API_KEY` secret.
4. Deploy.

## Option 2: Static Hosting (GitHub Pages, Vercel, Cloudflare Pages)
Because the repo includes an `index.html` configured for `stlite`, you can host the app on any static server.
1. Ensure `index.html`, `app.py`, and `main_data.csv` are in the root directory.
2. Deploy the root directory to your static host.
3. The app will download the Pyodide runtime and execute locally in the client's browser.
   *Note: In static mode, users must provide their own TMDB API key in the UI for posters, as there is no backend to securely store the key.*

## Option 3: Docker / Traditional VPS
A `Procfile` is included for standard PaaS (like Heroku or Render) deployments.
Run: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
