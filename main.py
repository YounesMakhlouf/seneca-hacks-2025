"""Entry point for the Body-to-Behavior Recommender API."""

from src.body_behavior_recommender.app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
