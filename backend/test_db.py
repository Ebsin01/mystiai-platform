import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="ai_palmistry",
        user="postgres",
        password="Maria15"
    )

    print("Connected Successfully!")

    cur = conn.cursor()
    cur.execute("SELECT current_database();")
    print(cur.fetchone())

    conn.close()

except Exception as e:
    print(e)