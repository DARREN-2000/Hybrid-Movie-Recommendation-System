const inputEl = document.getElementById('movie-input');
const listEl = document.getElementById('movie-titles');
const statusEl = document.getElementById('status');
const resultsEl = document.getElementById('results');
const resultsTitleEl = document.getElementById('results-title');
const recommendBtn = document.getElementById('recommend-btn');
const randomBtn = document.getElementById('random-btn');
const clearBtn = document.getElementById('clear-btn');
const DEFAULT_RECOMMENDATION_COUNT = 10;
const MAX_AUTOCOMPLETE_SUGGESTIONS = 3000;
const DATASET_PATH_CANDIDATES = ['./main_data.csv', '../main_data.csv'];

const state = {
  movies: [],
  byTitle: new Map(),
  invertedIndex: new Map(),
  loaded: false,
};

function normalize(value) {
  return String(value || '').trim().toLowerCase().replace(/\s+/g, ' ');
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < text.length; i += 1) {
    const c = text[i];
    const next = text[i + 1];

    if (c === '"') {
      if (inQuotes && next === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (c === ',' && !inQuotes) {
      row.push(current);
      current = '';
    } else if ((c === '\n' || c === '\r') && !inQuotes) {
      if (c === '\r' && next === '\n') i += 1;
      row.push(current);
      if (row.some((field) => field !== '')) rows.push(row);
      row = [];
      current = '';
    } else {
      current += c;
    }
  }

  if (current || row.length > 0) {
    row.push(current);
    rows.push(row);
  }

  return rows;
}

function createMovieObject(raw, headerMap, index) {
  const title = raw[headerMap.movie_title] || '';
  const genres = raw[headerMap.genres] || 'Unknown genres';
  const director = raw[headerMap.director_name] || 'Unknown director';
  const comb = normalize(raw[headerMap.comb]);
  const tokens = [...new Set(comb.split(' ').filter(Boolean))];

  return {
    index,
    title,
    normalizedTitle: normalize(title),
    genres,
    director,
    tokenSet: new Set(tokens),
  };
}

function buildIndexes() {
  state.byTitle.clear();
  state.invertedIndex.clear();

  state.movies.forEach((movie) => {
    const list = state.byTitle.get(movie.normalizedTitle) || [];
    list.push(movie.index);
    state.byTitle.set(movie.normalizedTitle, list);

    movie.tokenSet.forEach((token) => {
      const ids = state.invertedIndex.get(token) || new Set();
      ids.add(movie.index);
      state.invertedIndex.set(token, ids);
    });
  });
}

function chooseMovieIndex(titleInput) {
  const normalized = normalize(titleInput);
  const exact = state.byTitle.get(normalized);
  if (exact && exact.length) return exact[0];

  const candidates = state.movies
    .filter((movie) => movie.normalizedTitle.includes(normalized) || normalized.includes(movie.normalizedTitle))
    .slice(0, 1);

  return candidates.length ? candidates[0].index : -1;
}

function scoreSimilarity(baseMovie, candidateMovie) {
  const a = baseMovie.tokenSet;
  const b = candidateMovie.tokenSet;
  if (!a.size || !b.size) return 0;

  let overlap = 0;
  a.forEach((token) => {
    if (b.has(token)) overlap += 1;
  });

  return overlap / Math.sqrt(a.size * b.size);
}

function recommend(movieIndex, limit = DEFAULT_RECOMMENDATION_COUNT) {
  const movie = state.movies[movieIndex];
  if (!movie) return [];

  const candidateIds = new Set();
  movie.tokenSet.forEach((token) => {
    const ids = state.invertedIndex.get(token);
    if (!ids) return;
    ids.forEach((id) => {
      if (id !== movie.index) candidateIds.add(id);
    });
  });

  const scored = [];
  candidateIds.forEach((id) => {
    const candidate = state.movies[id];
    const score = scoreSimilarity(movie, candidate);
    if (score > 0) scored.push({ candidate, score });
  });

  scored.sort((a, b) => b.score - a.score || a.candidate.title.localeCompare(b.candidate.title));
  return scored.slice(0, limit);
}

function renderEmpty(message) {
  resultsEl.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
}

function renderRecommendations(seedMovie, recommendations) {
  resultsTitleEl.textContent = `Recommendations for "${seedMovie.title}"`;

  if (!recommendations.length) {
    renderEmpty('No similar movies were found. Try another title.');
    return;
  }

  const cards = recommendations.map(({ candidate, score }, idx) => `
    <article class="card">
      <h3>${idx + 1}. ${escapeHtml(candidate.title)}</h3>
      <p><strong>Genres:</strong> ${escapeHtml(candidate.genres)}</p>
      <p><strong>Director:</strong> ${escapeHtml(candidate.director)}</p>
      <p><strong>Similarity:</strong> ${(score * 100).toFixed(1)}%</p>
    </article>
  `);

  resultsEl.innerHTML = cards.join('');
}

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? '#b42318' : '';
}

function setControlsEnabled(enabled) {
  recommendBtn.disabled = !enabled;
  randomBtn.disabled = !enabled;
  clearBtn.disabled = !enabled;
}

async function fetchDatasetText() {
  for (const path of DATASET_PATH_CANDIDATES) {
    try {
      const response = await fetch(path);
      if (response.ok) return await response.text();
    } catch (error) {
      console.debug(`Dataset fetch failed for ${path}:`, error);
    }
  }
  throw new Error('Dataset file was not found at expected paths.');
}

function onRecommend() {
  if (!state.loaded) {
    setStatus('Dataset is still loading. Please wait.', true);
    return;
  }

  const query = inputEl.value;
  if (!query.trim()) {
    setStatus('Please enter a movie title first.', true);
    renderEmpty('Enter a movie title to see recommendations.');
    return;
  }

  const selectedIndex = chooseMovieIndex(query);
  if (selectedIndex === -1) {
    setStatus('Movie not found. Try a close title from suggestions.', true);
    renderEmpty('Movie not found in dataset.');
    return;
  }

  const seedMovie = state.movies[selectedIndex];
  inputEl.value = seedMovie.title;
  const recs = recommend(selectedIndex, DEFAULT_RECOMMENDATION_COUNT);
  setStatus(`Showing top ${recs.length} similar movies from ${state.movies.length.toLocaleString()} titles.`);
  renderRecommendations(seedMovie, recs);
}

function onRandomPick() {
  if (!state.loaded || !state.movies.length) return;
  const idx = Math.floor(Math.random() * state.movies.length);
  inputEl.value = state.movies[idx].title;
  onRecommend();
}

function onClear() {
  inputEl.value = '';
  setStatus('');
  resultsTitleEl.textContent = 'Recommendations';
  renderEmpty('Enter a movie title to see recommendations.');
}

async function init() {
  setControlsEnabled(false);
  setStatus('Loading movie dataset...');
  renderEmpty('Loading dataset, please wait...');

  try {
    const csvText = await fetchDatasetText();
    const rows = parseCsv(csvText);
    const header = rows.shift() || [];

    const headerMap = {
      movie_title: header.indexOf('movie_title'),
      genres: header.indexOf('genres'),
      director_name: header.indexOf('director_name'),
      comb: header.indexOf('comb'),
    };

    if (Object.values(headerMap).some((idx) => idx < 0)) {
      throw new Error('Dataset columns are missing.');
    }

    state.movies = rows
      .map((row, index) => createMovieObject(row, headerMap, index))
      .filter((movie) => movie.normalizedTitle && movie.tokenSet.size);

    buildIndexes();

    const titleSample = state.movies
      .slice(0, MAX_AUTOCOMPLETE_SUGGESTIONS)
      .map((movie) => `<option value="${escapeHtml(movie.title)}"></option>`)
      .join('');

    listEl.innerHTML = titleSample;
    state.loaded = true;
    setControlsEnabled(true);
    setStatus(`Ready. Loaded ${state.movies.length.toLocaleString()} movies.`);
    renderEmpty('Enter a movie title to see recommendations.');
  } catch (error) {
    setStatus(`Could not load app data: ${error.message}`, true);
    renderEmpty('Unable to load movie data. Check deployment paths and try again.');
  }
}

recommendBtn.addEventListener('click', onRecommend);
randomBtn.addEventListener('click', onRandomPick);
clearBtn.addEventListener('click', onClear);
inputEl.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') onRecommend();
});

init();
