import pytest
import pandas as pd
import numpy as np
import requests
from unittest.mock import patch, Mock
from app import resolve_title, build_movie_vectors, get_recommendations, fetch_poster


def test_resolve_title():
    titles = ["Toy Story", "Jumanji", "The Matrix"]
    assert resolve_title("toy story", titles) == "Toy Story"
    assert resolve_title("jumanji", titles) == "Jumanji"
    assert resolve_title("matrix", titles) == "The Matrix"
    assert resolve_title("unknown", titles) is None


def test_get_recommendations():
    data = {
        "movie_title": ["Movie A", "Movie B", "Movie C"],
        "comb": ["action adventure", "action adventure", "romance comedy"],
    }
    df = pd.DataFrame(data)
    matrix = build_movie_vectors(df["comb"])
    recs = get_recommendations("Movie A", df, matrix, top_n=1)
    assert len(recs) == 1
    assert recs[0]["movie_title"] == "Movie B"


@patch("app.requests.get")
def test_fetch_poster_success(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"results": [{"poster_path": "/fake_poster.jpg"}]}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    poster_url = fetch_poster("Inception", "fake_api_key")

    assert poster_url == "https://image.tmdb.org/t/p/w500/fake_poster.jpg"
    mock_get.assert_called_once_with(
        "https://api.themoviedb.org/3/search/movie",
        params={"api_key": "fake_api_key", "query": "Inception"},
        timeout=5,
    )


@patch("app.requests.get")
def test_fetch_poster_failure(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("API Error")

    poster_url = fetch_poster("Inception", "fake_api_key")

    assert poster_url is None
    mock_get.assert_called_once_with(
        "https://api.themoviedb.org/3/search/movie",
        params={"api_key": "fake_api_key", "query": "Inception"},
        timeout=5,
    )


def test_fetch_poster_no_api_key():
    poster_url = fetch_poster("Inception", "")
    assert poster_url is None
