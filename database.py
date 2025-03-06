import psycopg2

# PostgreSQL Connection (Replace with your Railway Database URL)
DB_URL = "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"

def create_table():
    """Create the subscribers table if it does not exist."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            chat_id BIGINT PRIMARY KEY
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def add_subscriber(chat_id):
    """Add a user to the subscribers list."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("INSERT INTO subscribers (chat_id) VALUES (%s) ON CONFLICT DO NOTHING;", (chat_id,))
    conn.commit()
    cur.close()
    conn.close()

def remove_subscriber(chat_id):
    """Remove a user from the subscribers list."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("DELETE FROM subscribers WHERE chat_id = %s;", (chat_id,))
    conn.commit()
    cur.close()
    conn.close()

def get_subscribers():
    """Retrieve all subscribed users."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM subscribers;")
    subscribers = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return subscribers

# Create the table when script runs
if __name__ == "__main__":
    create_table()
