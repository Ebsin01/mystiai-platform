from app.database import engine

with engine.connect() as conn:
    result = conn.exec_driver_sql("SELECT current_database();")
    print("Database:", result.fetchone()[0])

    result = conn.exec_driver_sql("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='palm_analyses'
        ORDER BY ordinal_position;
    """)

    print("\nColumns:")
    for row in result:
        print(row[0])