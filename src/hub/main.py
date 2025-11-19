import uvicorn
from src.hub.api import app

if __name__ == "__main__":
    uvicorn.run("src.hub.api:app", host="0.0.0.0", port=8000, reload=True)
