from utils.api_client import get_scorecard
from utils.db_connection import get_connection

def get_first_match_id():
    """
    Get one match ID from the local database.
    """
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

def main():
    match_id = get_first_match_id()
    if not match_id:
        print("No matches found in the database.")
        return
    print(f"Testing scorecard for Match ID: {match_id}")
    data = get_scorecard(match_id)
    print("\nScorecard API Response:")
    print(type(data))
    if isinstance(data, dict):
        print("\nTop-level keys:")
        print(data.keys())
    print("\nAPI test successful.")

if __name__ == "__main__":
    main()