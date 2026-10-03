import sqlite3

def init_db():
    # 1. ESTABLISH CONNECTION
    # This creates a permanent, local database file named 'url_storage.db' 
    # inside your project folder.
    conn = sqlite3.connect("url_storage.db")
    cursor = conn.cursor()

    # 2. CREATE THE MASTER LEDGER TABLE
    # We define strict column definitions and constraints to guarantee data integrity.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            short_code TEXT PRIMARY KEY,
            long_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            clicks INTEGER DEFAULT 0,
            password_hash TEXT
        )
    """)

    # 3. INTERVIEW X-FACTOR: SPEED OPTIMIZATION (INDEXING)
    # Interview Hack: Databases search row-by-row. By creating an INDEX on short_code,
    # lookups drop from O(N) linear time to O(log N) logarithmic time. 
    # This ensures your app stays blazing fast even with 10 million shortened links!
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_short_code ON urls(short_code)")

    # 4. COMMIT AND CLOSE THE GATEWAY
    conn.commit()
    conn.close()
    print("🚀 Database initialized successfully with Performance Indexing!")

# Run the function when this specific script is executed
if __name__ == "__main__":
    init_db()
