from fastapi import FastAPI

# 1. INITIALIZE THE APPLICATION
# This creates your master web app instance. Think of this as turning on the engine 
# of your corporate web server.
app = FastAPI(
    title="Smart URL Shortener API",
    description="Production-grade URL shortening backend system",
    version="1.0.0"
)

# 2. CREATE A ROOT ENTRY ENDPOINT (HTTP GET)
# This is a public pathway. When someone visits the home URL of your application 
# in a browser, this function triggers automatically.
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to the Smart URL Shortener API Engine!",
        "documentation_path": "/docs"
    }
