import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from security import check_url_safety

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
        # RUN SECURITY CHECKPOINT BEFORE STORING ANYTHING IN THE VAULT
    is_safe = check_url_safety(request.long_url)
    if not is_safe:
        raise HTTPException(
            status_code=400, 
            detail="Security Risk Alert: This URL has been flagged as malicious by Google Safe Browsing."
        )

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
from fastapi.responses import RedirectResponse

# =====================================================================
# THE REDIRECTION & REAL-TIME ANALYTICS ROUTER (HTTP GET)
# This path parameter listener intercepts ANY trailing short code token
# typed into the home domain and routes the browser dynamically.
# =====================================================================
@app.get("/{short_code}")
def redirect_to_target(short_code: str):
    # 1. Establish an active gateway channel to the binary storage vault
    conn = sqlite3.connect("url_storage.db")
    cursor = conn.cursor()
    
    # 2. Database Lookup Transaction
    # Search the ledger row matching the incoming short_code token
    cursor.execute("SELECT long_url, clicks FROM urls WHERE short_code = ?", (short_code,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        # Defensive Error Handling: Guard against invalid or dead link inputs
        raise HTTPException(status_code=404, detail="Short URL not found or has expired")
        
    original_long_url = row[0]
    
    # 3. ANALYTICS ENGINE LAYER
    # Update the data row state, incrementing total traffic metrics atomically
    try:
        cursor.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?", 
            (short_code,)
        )
        conn.commit()
    except Exception as e:
        # Graceful failure handling: close the stream if the update loops drop
        conn.close()
        raise HTTPException(status_code=500, detail=f"Analytics logging error: {str(e)}")
        
    conn.close()
    
    # 4. EXECUTING PROTOCOL ROUTING (HTTP 302 REDIRECT)
    # Commands the external browser engine to change its target address destination
    return RedirectResponse(url=original_long_url, status_code=302)
