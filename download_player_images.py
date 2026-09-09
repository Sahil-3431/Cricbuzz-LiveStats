import requests
import re
import time
import hashlib
import html
import tomllib
from pathlib import Path
from urllib.parse import quote

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
SECRETS_FILE = (
    BASE_DIR
    / ".streamlit"
    / "secrets.toml"
)
IMAGE_FOLDER = (
    BASE_DIR
    / "assets"
    / "players"
)
IMAGE_FOLDER.mkdir(parents=True,exist_ok=True)

# =========================================================
# LOAD API SETTINGS
# =========================================================

with open(SECRETS_FILE, "rb") as file:
    secrets = tomllib.load(file)

API_KEY = secrets["RAPIDAPI_KEY"]
API_HOST = secrets["RAPIDAPI_HOST"]
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

WEB_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,"
        "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.cricbuzz.com/"
}

# =========================================================
# RAPIDAPI RANKINGS
# =========================================================

def get_rankings(format_type, category):
    if category == "batting":
        url = (
            "https://cricbuzz-cricket.p.rapidapi.com/"
            "stats/v1/rankings/batsmen"
        )
    else:
        url = (
            "https://cricbuzz-cricket.p.rapidapi.com/"
            "stats/v1/rankings/bowlers"
        )
    params = {"formatType": format_type}
    response = requests.get(url,headers=HEADERS,params=params,timeout=30)
    response.raise_for_status()
    return response.json()

# =========================================================
# GET PLAYER LIST
# =========================================================

def get_players():
    print()
    print("Fetching ODI batting rankings...")
    batting_data = get_rankings("odi","batting")
    print()
    print("Fetching ODI bowling rankings...")
    bowling_data = get_rankings("odi","bowling")
    players = {}

    # -----------------------------------------------------
    # BATTING PLAYERS
    # -----------------------------------------------------

    for player in batting_data.get("rank", []):
        player_id = player.get("id")
        player_name = player.get("name")
        if player_id and player_name:
            players[str(player_id)] = {
                "id": str(player_id),
                "name": player_name
            }

    # -----------------------------------------------------
    # BOWLING PLAYERS
    # -----------------------------------------------------

    for player in bowling_data.get("rank", []):
        player_id = player.get("id")
        player_name = player.get("name")
        if player_id and player_name:
            players[str(player_id)] = {
                "id": str(player_id),
                "name": player_name
            }
    return list(players.values())

# =========================================================
# CREATE CRICBUZZ PROFILE URL
# =========================================================

def make_slug(name):
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+","-",slug)
    slug = slug.strip("-")
    return slug

def get_profile_url(player_id, player_name):
    slug = make_slug(player_name)
    return (
        f"https://www.cricbuzz.com/"
        f"profiles/{player_id}/{slug}"
    )

# =========================================================
# FIND PLAYER IMAGE
# =========================================================

def find_player_image(page_html,player_id,player_name):

    # Decode HTML entities
    page_html = html.unescape(page_html)

    # -----------------------------------------------------
    # METHOD 1
    # Search for image URL containing player's slug
    # -----------------------------------------------------

    slug = make_slug(player_name)
    pattern = re.compile(
        r'https://static\.cricbuzz\.com/'
        r'a/img/[^"\']+'
        + re.escape(slug)
        + r'[^"\']*',
        re.IGNORECASE
    )
    matches = pattern.findall(page_html)
    if matches:
        return clean_image_url(matches[0])

    # -----------------------------------------------------
    # METHOD 2
    # Find <img ... alt="player name" ...>
    # -----------------------------------------------------

    img_tags = re.findall(
        r"<img\b[^>]*>",
        page_html,
        re.IGNORECASE
    )
    for tag in img_tags:
        tag_lower = tag.lower()
        if slug in tag_lower:
            urls = re.findall(
                r'https://static\.cricbuzz\.com/'
                r'a/img/[^"\']+',
                tag,
                re.IGNORECASE
            )
            if urls:
                return clean_image_url(urls[0])

    # -----------------------------------------------------
    # METHOD 3
    # Search around player name
    # -----------------------------------------------------

    name_lower = player_name.lower()
    position = page_html.lower().find(name_lower)
    if position != -1:
        start = max(0,position - 5000)
        end = min(len(page_html),position + 5000)
        nearby_html = page_html[start:end]
        urls = re.findall(
            r'https://static\.cricbuzz\.com/'
            r'a/img/[^"\']+',
            nearby_html,
            re.IGNORECASE
        )
        for url in urls:
            url = clean_image_url(url)
            if is_valid_player_image(url):
                return url

    # -----------------------------------------------------
    # METHOD 4
    # Extract all static.cricbuzz images
    # and reject generic placeholder
    # -----------------------------------------------------

    urls = re.findall(
        r'https://static\.cricbuzz\.com/'
        r'a/img/[^"\']+',
        page_html,
        re.IGNORECASE
    )
    for url in urls:
        url = clean_image_url(url)
        if is_valid_player_image(url):
            return url
    return None

# =========================================================
# CLEAN URL
# =========================================================

def clean_image_url(url):
    url = html.unescape(url)

    # Remove escaped characters
    url = url.replace(
        "\\/",
        "/"
    )
    # Remove HTML entities
    url = url.replace("&amp;","&")
    return url.strip()

# =========================================================
# REJECT GENERIC CRICBUZZ IMAGE
# =========================================================

def is_valid_player_image(url):
    if not url:
        return False
    url_lower = url.lower()

    # Known generic placeholder
    bad_parts = ["c582022/i.jpg","/i.jpg?d=high","/i.jpg?d=low"]
    for bad in bad_parts:
        if bad in url_lower:
            return False
    return True

# =========================================================
# DOWNLOAD IMAGE
# =========================================================

def download_image(image_url,player_id,player_name):
    try:
        response = requests.get(image_url,headers=WEB_HEADERS,timeout=20)
        response.raise_for_status()
        content = response.content

        # -------------------------------------------------
        # Verify actual image
        # -------------------------------------------------

        if not (
            content.startswith(b"\xff\xd8\xff")
            or content.startswith(b"\x89PNG")
            or content.startswith(b"RIFF")
        ):
            print("✗ Response is not an image")
            return False, None

        # -------------------------------------------------
        # Reject tiny placeholder images
        # -------------------------------------------------

        if len(content) < 3000:
            print(
                "✗ Image too small - "
                "possible placeholder"
            )
            return False, None

        # -------------------------------------------------
        # Save
        # -------------------------------------------------

        file_path = (IMAGE_FOLDER / f"{player_id}.jpg")
        with open(file_path,"wb") as file:
            file.write(content)

        # -------------------------------------------------
        # Hash for duplicate detection
        # -------------------------------------------------

        image_hash = hashlib.md5(content).hexdigest()
        return True, image_hash
    except Exception as error:
        print(f"✗ Download failed: {error}")
        return False, None

# =========================================================
# PROCESS ONE PLAYER
# =========================================================

def process_player(player,downloaded_hashes):
    player_id = player["id"]
    player_name = player["name"]
    print()
    print(
        f"Processing: "
        f"{player_name} ({player_id})"
    )
    profile_url = get_profile_url(player_id,player_name)
    print(f"Profile: {profile_url}")
    try:
        response = requests.get(profile_url,headers=WEB_HEADERS,timeout=20)
        response.raise_for_status()
        page_html = response.text
    except Exception as error:
        print(f"✗ Profile page failed: {error}")
        return False
    
    image_url = find_player_image(page_html,player_id,player_name)
    if not image_url:
        print(
            "✗ Player-specific image "
            "not found"
        )
        return False

    print("Image URL found:")
    print(image_url)

    # -----------------------------------------------------
    # Reject generic image
    # -----------------------------------------------------

    if not is_valid_player_image(image_url):
        print(
            "✗ Generic Cricbuzz image "
            "detected - skipped"
        )
        return False
    success, image_hash = download_image(image_url,player_id,player_name)
    if not success:
        return False

    # -----------------------------------------------------
    # Duplicate image detection
    # -----------------------------------------------------

    if image_hash in downloaded_hashes:
        old_player = downloaded_hashes[image_hash]
        print("⚠ WARNING:")
        print(
            f"Same image as "
            f"{old_player}"
        )
    else:
        downloaded_hashes[image_hash] = player_name

    print(
        f"✓ Downloaded: "
        f"{player_name} ({player_id})"
    )
    return True

# =========================================================
# MAIN
# =========================================================

def main():
    print("=" * 60)
    print("CRICBUZZ PLAYER IMAGE DOWNLOADER")
    print("=" * 60)

    # -----------------------------------------------------
    # Get players
    # -----------------------------------------------------

    players = get_players()

    print()
    print(
        f"Total unique players: "
        f"{len(players)}"
    )

    # -----------------------------------------------------
    # Track hashes
    # -----------------------------------------------------

    downloaded_hashes = {}
    success_count = 0
    failed_players = []

    # -----------------------------------------------------
    # Download
    # -----------------------------------------------------

    for index, player in enumerate(players,start=1):
        print()
        print(
            f"[{index}/{len(players)}] "
            f"{player['name']} "
            f"({player['id']})"
        )
        success = process_player(player,downloaded_hashes)
        if success:
            success_count += 1
        else:
            failed_players.append(player)
        # Small delay
        time.sleep(1)

    # =====================================================
    # FINAL REPORT
    # =====================================================

    print()
    print("=" * 60)
    print(
        f"Images downloaded: "
        f"{success_count}"
    )
    print(
        f"Images unavailable: "
        f"{len(failed_players)}"
    )

    if failed_players:
        print()
        print("Failed players:")
        for player in failed_players:
            print(
                f"- {player['name']} "
                f"({player['id']})"
            )

    print()
    print(
        f"Image folder: "
        f"{IMAGE_FOLDER}"
    )
    print("=" * 60)

    # -----------------------------------------------------
    # Duplicate warning
    # -----------------------------------------------------

    unique_hashes = len(downloaded_hashes)
    print()
    print(
        f"Unique image hashes: "
        f"{unique_hashes}"
    )
    if unique_hashes != success_count:
        print()
        print("⚠ WARNING:")
        print(
            "Some players have identical "
            "image files."
        )
    else:
        print()
        print(
            "✓ All downloaded images "
            "are unique."
        )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()