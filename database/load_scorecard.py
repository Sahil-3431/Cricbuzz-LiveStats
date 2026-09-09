from utils.api_client import get_scorecard
from utils.db_connection import get_connection

def get_first_match_id():
    """Get the most recent match ID from the database."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT match_id
        FROM matches
        ORDER BY start_date DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    connection.close()
    if row:
        return row["match_id"]
    return None

def get_match_teams(match_id):
    """Get both teams associated with a match."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            t1.team_id AS team1_id,
            t1.team_name AS team1_name,
            t2.team_id AS team2_id,
            t2.team_name AS team2_name
        FROM matches m
        LEFT JOIN teams t1
            ON m.team1_id = t1.team_id
        LEFT JOIN teams t2
            ON m.team2_id = t2.team_id
        WHERE m.match_id = ?
    """, (match_id,))
    row = cursor.fetchone()
    connection.close()
    return row

def find_team_id(team_name, match_teams):
    """Find the database team ID using the API team name."""
    if not team_name or not match_teams:
        return None
    team_name = team_name.strip().lower()
    team1_name = (
        match_teams["team1_name"] or ""
    ).strip().lower()
    team2_name = (
        match_teams["team2_name"] or ""
    ).strip().lower()
    if team_name == team1_name:
        return match_teams["team1_id"]
    if team_name == team2_name:
        return match_teams["team2_id"]
    if team_name in team1_name or team1_name in team_name:
        return match_teams["team1_id"]
    if team_name in team2_name or team2_name in team_name:
        return match_teams["team2_id"]
    return None

def get_opposite_team_id(team_id, match_teams):
    """Return the opposing team's ID."""
    if not match_teams or team_id is None:
        return None
    if team_id == match_teams["team1_id"]:
        return match_teams["team2_id"]
    if team_id == match_teams["team2_id"]:
        return match_teams["team1_id"]
    return None

def insert_player(cursor, player_id, player_name, role=None):
    """Insert a player if the player does not already exist."""
    cursor.execute("""
        INSERT OR IGNORE INTO players (
            player_id,
            player_name,
            role
        )
        VALUES (?, ?, ?)
    """, (
        player_id,
        player_name,
        role
    ))

def update_player_role(cursor, player_id, role):
    """Update a player's role."""
    if not player_id or not role:
        return
    cursor.execute("""
        UPDATE players
        SET role = ?
        WHERE player_id = ?
    """, (
        role,
        player_id
    ))

def insert_match_player(cursor, match_id, player_id, team_id):
    """Connect a player with a match and team."""
    if team_id is None:
        return
    cursor.execute("""
        INSERT OR IGNORE INTO match_players (
            match_id,
            player_id,
            team_id
        )
        VALUES (?, ?, ?)
    """, (
        match_id,
        player_id,
        team_id
    ))

def load_batting_scorecard(cursor,match_id,innings_number,batsmen,batting_team_id):
    """Load batting scorecard data."""
    if not batsmen:
        return 0
    batting_position = 1
    batting_player_ids = []
    for batsman in batsmen:
        player_id = batsman.get("id")
        player_name = batsman.get("name")
        if not player_id or not player_name:
            continue
        runs = batsman.get("runs", 0)
        balls = batsman.get("balls", 0)
        fours = batsman.get("fours", 0)
        sixes = batsman.get("sixes", 0)
        strike_rate = batsman.get("strkrate")
        try:
            strike_rate = float(strike_rate)
        except (TypeError, ValueError):
            strike_rate = None
        insert_player(
            cursor,
            player_id,
            player_name,
            role="Batsman"
        )
        insert_match_player(
            cursor,
            match_id,
            player_id,
            batting_team_id
        )
        cursor.execute("""
            INSERT INTO batting_scorecard (
                match_id,
                player_id,
                innings_number,
                batting_position,
                runs,
                balls,
                fours,
                sixes,
                strike_rate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match_id,
            player_id,
            innings_number,
            batting_position,
            runs,
            balls,
            fours,
            sixes,
            strike_rate
        ))
        batting_player_ids.append(player_id)
        batting_position += 1
    return batting_player_ids

def load_bowling_scorecard(cursor,match_id,innings_number,bowlers,bowling_team_id):
    """Load bowling scorecard data."""
    if not bowlers:
        return 0
    bowling_player_ids = []
    for bowler in bowlers:
        player_id = bowler.get("id")
        player_name = bowler.get("name")
        if not player_id or not player_name:
            continue
        overs = bowler.get("overs", "0")
        maidens = bowler.get("maidens", 0)
        runs_conceded = bowler.get("runs", 0)
        wickets = bowler.get("wickets", 0)
        economy_rate = bowler.get("economy")
        try:
            economy_rate = float(economy_rate)
        except (TypeError, ValueError):
            economy_rate = None
        insert_player(
            cursor,
            player_id,
            player_name,
            role="Bowler"
        )
        insert_match_player(
            cursor,
            match_id,
            player_id,
            bowling_team_id
        )
        cursor.execute("""
            INSERT INTO bowling_scorecard (
                match_id,
                player_id,
                innings_number,
                overs,
                maidens,
                runs_conceded,
                wickets,
                economy_rate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match_id,
            player_id,
            innings_number,
            overs,
            maidens,
            runs_conceded,
            wickets,
            economy_rate
        ))
        bowling_player_ids.append(player_id)
    return bowling_player_ids

def load_partnerships(cursor,match_id,innings_number,partnership_data):
    """Load partnership information."""
    if not partnership_data:
        return 0
    partnership_count = 0

    for partnership in partnership_data:
        batsman1_id = partnership.get("bat1id")
        batsman1_name = partnership.get("bat1name")
        batsman2_id = partnership.get("bat2id")
        batsman2_name = partnership.get("bat2name")
        if not batsman1_id or not batsman2_id:
            continue
        insert_player(cursor,batsman1_id,batsman1_name)
        insert_player(cursor,batsman2_id,batsman2_name)
        cursor.execute("""
            INSERT INTO partnerships (
                match_id,
                innings_number,
                batsman1_id,
                batsman1_name,
                batsman2_id,
                batsman2_name,
                batsman1_runs,
                batsman1_balls,
                batsman2_runs,
                batsman2_balls,
                partnership_runs,
                partnership_balls
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match_id,
            innings_number,
            batsman1_id,
            batsman1_name,
            batsman2_id,
            batsman2_name,
            partnership.get("bat1runs", 0),
            partnership.get("bat1balls", 0),
            partnership.get("bat2runs", 0),
            partnership.get("bat2balls", 0),
            partnership.get("totalruns", 0),
            partnership.get("totalballs", 0)
        ))
        partnership_count += 1
    return partnership_count

def update_player_roles(cursor,batting_player_ids,bowling_player_ids):
    """
    Determine match-based player roles.
    Player appearing in both batting and bowling:
        All-rounder
    Player appearing only while batting:
        Batsman
    Player appearing only while bowling:
        Bowler
    """
    batting_set = set(batting_player_ids)
    bowling_set = set(bowling_player_ids)
    all_player_ids = batting_set | bowling_set
    for player_id in all_player_ids:
        if player_id in batting_set and player_id in bowling_set:
            role = "All-rounder"
        elif player_id in batting_set:
            role = "Batsman"
        else:
            role = "Bowler"
        update_player_role(cursor,player_id,role)

def clear_existing_scorecard(cursor, match_id):
    """Remove previously loaded scorecard data for a match."""
    cursor.execute("""
        DELETE FROM batting_scorecard
        WHERE match_id = ?
    """, (match_id,))

    cursor.execute("""
        DELETE FROM bowling_scorecard
        WHERE match_id = ?
    """, (match_id,))

    cursor.execute("""
        DELETE FROM match_players
        WHERE match_id = ?
    """, (match_id,))

    cursor.execute("""
        DELETE FROM partnerships
        WHERE match_id = ?
    """, (match_id,))

def load_scorecard(match_id):
    """Fetch and load a match scorecard into SQLite."""
    print(f"Fetching scorecard for Match ID: {match_id}")
    data = get_scorecard(match_id)
    scorecard = data.get("scorecard")
    if not isinstance(scorecard, list):
        raise ValueError(
            "Unexpected scorecard format. "
            "Expected a list of innings."
        )
    match_teams = get_match_teams(match_id)
    if not match_teams:
        raise ValueError(f"Match {match_id} was not found in database.")
    connection = get_connection()
    cursor = connection.cursor()
    total_batting_rows = 0
    total_bowling_rows = 0
    total_partnership_rows = 0
    all_batting_player_ids = []
    all_bowling_player_ids = []

    try:
        clear_existing_scorecard(cursor,match_id)
        for innings in scorecard:
            innings_number = innings.get("inningsid")
            try:
                innings_number = int(innings_number)
            except (TypeError, ValueError):
                continue
            batting_team_name = innings.get("batteamname")
            batting_team_id = find_team_id(batting_team_name,match_teams)
            bowling_team_id = get_opposite_team_id(batting_team_id,match_teams)
            batsmen = innings.get("batsman",[])
            bowlers = innings.get("bowler",[])
            batting_player_ids = load_batting_scorecard(
                cursor,
                match_id,
                innings_number,
                batsmen,
                batting_team_id
            )
            bowling_player_ids = load_bowling_scorecard(
                cursor,
                match_id,
                innings_number,
                bowlers,
                bowling_team_id
            )
            partnership_object = innings.get("partnership",{})
            partnerships = partnership_object.get("partnership",[])
            partnership_rows = load_partnerships(
                cursor,
                match_id,
                innings_number,
                partnerships
            )
            all_batting_player_ids.extend(batting_player_ids)
            all_bowling_player_ids.extend(bowling_player_ids)
            total_batting_rows += len(batting_player_ids)
            total_bowling_rows += len(bowling_player_ids)
            total_partnership_rows += partnership_rows

        update_player_roles(
            cursor,
            all_batting_player_ids,
            all_bowling_player_ids
        )
        connection.commit()
        print("\nScorecard loaded successfully.")
        print(
            f"Batting rows inserted: "
            f"{total_batting_rows}"
        )
        print(
            f"Bowling rows inserted: "
            f"{total_bowling_rows}"
        )
        print(
            f"Partnership rows inserted: "
            f"{total_partnership_rows}"
        )
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def main():
    """Load the scorecard for the latest match."""
    match_id = get_first_match_id()
    if not match_id:
        print("No matches found in database.")
        return
    try:
        load_scorecard(match_id)
    except Exception as error:
        print(f"\nError loading scorecard: {error}")

if __name__ == "__main__":
    main()