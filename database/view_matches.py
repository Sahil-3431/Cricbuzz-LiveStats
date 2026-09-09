from utils.db_connection import get_connection

connection = get_connection()
cursor = connection.cursor()
cursor.execute("""
    SELECT
        matches.match_id,
        series.series_name,
        matches.match_description,
        matches.match_format,
        matches.state,
        matches.status
    FROM matches
    LEFT JOIN series
        ON matches.series_id = series.series_id
    ORDER BY matches.start_date DESC
""")
matches = cursor.fetchall()
print("\nStored Matches:\n")
for match in matches:
    print(f"Match ID: {match['match_id']}")
    print(f"Series: {match['series_name']}")
    print(f"Description: {match['match_description']}")
    print(f"Format: {match['match_format']}")
    print(f"State: {match['state']}")
    print(f"Status: {match['status']}")
    print("-" * 60)

connection.close()