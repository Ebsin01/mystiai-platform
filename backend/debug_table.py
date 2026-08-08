from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://postgres:Maria15@localhost:5432/ai_palmistry"
)

with engine.connect() as conn:
    print(conn.execute(text("SELECT current_database()")).scalar())
    print(conn.execute(text("SELECT current_schema()")).scalar())

    result = conn.execute(text("""
        SELECT *
        FROM palm_analyses
        LIMIT 1
    """))

    print(result.keys())