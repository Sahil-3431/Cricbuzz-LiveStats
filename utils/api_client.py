import re
from urllib.parse import (
    parse_qs,
    urlencode,
    urlparse,
    urlunparse
)

import requests
import streamlit as st


API_HOST = st.secrets["RAPIDAPI_HOST"]
API_KEY = st.secrets["RAPIDAPI_KEY"]
SCORECARD_API_URL = st.secrets["SCORECARD_API_URL"]


def get_headers():
    """Return RapidAPI headers."""
    return {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }


def get_live_matches():
    """Fetch live matches."""

    url = (
        "https://cricbuzz-cricket.p.rapidapi.com/"
        "matches/v1/live"
    )

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def build_scorecard_url(match_id):
    """
    Build the correct scorecard URL for a match.

    Handles:
    - {matchId}
    - ?matchId=123
    - URL ending with /123
    - fallback query parameter
    """

    match_id = str(match_id)
    base_url = SCORECARD_API_URL.strip()

    # ----------------------------------------
    # 1. {matchId} placeholder
    # ----------------------------------------

    if "{matchId}" in base_url:
        return base_url.replace(
            "{matchId}",
            match_id
        )

    # ----------------------------------------
    # Parse URL
    # ----------------------------------------

    parsed = urlparse(base_url)

    query_params = parse_qs(
        parsed.query,
        keep_blank_values=True
    )

    # ----------------------------------------
    # 2. matchId already exists in query
    # ----------------------------------------

    if "matchId" in query_params:

        query_params["matchId"] = [
            match_id
        ]

        new_query = urlencode(
            query_params,
            doseq=True
        )

        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))

    # ----------------------------------------
    # 3. Match ID exists at end of URL path
    #
    # Example:
    #
    # /mcenter/v1/142539
    #
    # becomes:
    #
    # /mcenter/v1/169310
    # ----------------------------------------

    path = parsed.path

    if re.search(
        r"/\d+/?$",
        path
    ):

        new_path = re.sub(
            r"/\d+/?$",
            f"/{match_id}",
            path
        )

        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            new_path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))

    # ----------------------------------------
    # 4. No match ID found
    # Add query parameter
    # ----------------------------------------

    query_params["matchId"] = [
        match_id
    ]

    new_query = urlencode(
        query_params,
        doseq=True
    )

    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))


def get_scorecard(match_id):
    """Fetch scorecard for the selected match."""

    url = build_scorecard_url(
        match_id
    )

    print("=" * 60)
    print(
        f"REQUESTED MATCH ID: {match_id}"
    )
    print(
        f"SCORECARD URL: {url}"
    )
    print("=" * 60)

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data

def get_batting_rankings(format_type="odi"):
    """
    Fetch batting rankings from Cricbuzz API.
    """
    url = (
        "https://cricbuzz-cricket.p.rapidapi.com/"
        "stats/v1/rankings/batsmen"
    )

    params = {
        "formatType": format_type
    }

    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
        timeout=30
    )

    response.raise_for_status()
    return response.json()


def get_bowling_rankings(format_type="odi"):
    """
    Fetch bowling rankings from Cricbuzz API.
    """
    url = (
        "https://cricbuzz-cricket.p.rapidapi.com/"
        "stats/v1/rankings/bowlers"
    )

    params = {
        "formatType": format_type
    }

    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
        timeout=30
    )

    response.raise_for_status()
    return response.json()

def get_player_profile(player_id):
    """
    Fetch detailed information for a player.
    """

    if not player_id:
        raise ValueError("Player ID is required.")

    url = (
        "https://cricbuzz-cricket.p.rapidapi.com/"
        f"stats/v1/player/{player_id}"
    )

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def get_player_batting_stats(player_id):
    """
    Fetch detailed batting statistics for a player.
    """

    if not player_id:
        raise ValueError("Player ID is required.")

    url = (
        "https://cricbuzz-cricket.p.rapidapi.com/"
        f"stats/v1/player/{player_id}/batting"
    )

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def get_player_bowling_stats(player_id):
    """
    Fetch detailed bowling statistics for a player.
    """

    if not player_id:
        raise ValueError("Player ID is required.")

    url = (
        "https://cricbuzz-cricket.p.rapidapi.com/"
        f"stats/v1/player/{player_id}/bowling"
    )

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=30
    )

    response.raise_for_status()

    return response.json()