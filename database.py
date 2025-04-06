import psycopg2

# Database connection
DB_URL = "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"

def connect_db():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(DB_URL, sslmode="require")

def add_subscriber(chat_id, instrument):
    """Subscribe a user to a specific instrument."""
    conn = connect_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO subscribers (chat_id, instrument) VALUES (%s, LOWER(%s)) ON CONFLICT DO NOTHING;",
            (chat_id, instrument)
        )
        conn.commit()
    except Exception as e:
        print(f"Error adding subscriber: {e}")
    finally:
        cur.close()
        conn.close()

def remove_subscriber(chat_id, instrument):
    """Unsubscribe a user from a specific instrument."""
    conn = connect_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "DELETE FROM subscribers WHERE chat_id = %s AND instrument = LOWER(%s);",
            (chat_id, instrument)
        )
        conn.commit()
    except Exception as e:
        print(f"Error removing subscriber: {e}")
    finally:
        cur.close()
        conn.close()

def get_subscribers(instrument):
    """Get all users subscribed to a specific instrument."""
    conn = connect_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT chat_id FROM subscribers WHERE LOWER(instrument) = LOWER(%s);", (instrument,))
        subscribers = [row[0] for row in cur.fetchall()]
        return subscribers
    except Exception as e:
        print(f"Error retrieving subscribers: {e}")
        return []
    finally:
        cur.close()
        conn.close()
