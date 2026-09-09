from utils.db_connection import get_connection


connection = get_connection()

cursor = connection.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""")

tables = cursor.fetchall()

print("\nDatabase Tables:")

for table in tables:
    print("-", table["name"])

connection.close()