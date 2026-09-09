from utils.api_client import (
    get_player_profile,
    get_player_batting_stats,
    get_player_bowling_stats
)

import json


PLAYER_ID = "11808"


print("=" * 70)
print("PLAYER PROFILE")
print("=" * 70)

profile = get_player_profile(PLAYER_ID)

print(json.dumps(profile, indent=2)[:5000])


print()
print("=" * 70)
print("PLAYER BATTING STATS")
print("=" * 70)

batting = get_player_batting_stats(PLAYER_ID)

print(json.dumps(batting, indent=2)[:5000])


print()
print("=" * 70)
print("PLAYER BOWLING STATS")
print("=" * 70)

bowling = get_player_bowling_stats(PLAYER_ID)

print(json.dumps(bowling, indent=2)[:5000])