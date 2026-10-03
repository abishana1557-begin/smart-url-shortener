import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 1. IMPORT YOUR CUSTOM GEARS
# We import the conversion function from encoder.py and the database setup from database.py
from encoder import encode_id
from database import init_db

app = FastAPI(title="Smart URL Shortener Engine")

# Ensure the database table and performance indexes exist when the web server boots up
init_db()

# 2. DEFINE THE DATA ENTERING THE SYSTEM
# Pydantic maps out what incoming internet requests must look like.
# It enforces that the frontend MUST send an object containing a string called 'long_url'.
class URLRequest(BaseModel):
    long_url: str


@app.get("/")
def read_root():
    return {"status": "online", "message": "API Engine Connected to Database & Encoder"}


# 3. THE CONNECTED /SHORTEN ENDPOINT
# This is the pipeline where your database vault and math brain shake hands.
@app.post("/shorten")
def shorten_url(request: URLRequest):
    # Connect directly to our local relational database ledger file
    conn = sqlite3.connect("url_storage.db")
    cursor = conn.cursor()
    
    try:
        # A) Insert the long URL into the vault. 
        # By leaving short_code empty initially, SQLite auto-increments the row ID number.
        cursor.execute(
            "INSERT INTO urls (short_code, long_url) VALUES (?, ?)", 
            ("", request.long_url)
        )
        conn.commit()
        
        # B) Grab the unique auto-incremented database ID number that was just generated
        db_id = cursor.lastrowid
        
        # C) Run the database ID number straight through our Math Encoder Brain!
        short_token = encode_id(db_id)
        
        # D) Update the database row, replacing the blank space with our clean short token
        cursor.execute(
            "UPDATE urls SET short_code = ? WHERE rowid = ?", 
            (short_token, db_id)
        )
        conn.commit()
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database Insertion Error: {str(e)}")
    
    conn.close()
    
    # Return the final short URL path to the user!
    return {
        "original_url": request.long_url,
        "short_code": short_token,
        "short_url": f"http://127.0.0{short_token}"
    }
