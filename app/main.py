from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import gzip
import joblib
import pandas as pd

# Initialize FastAPI app
app = FastAPI(
    title="Movie Recommendation API",
    description="API for getting movie recommendations based on similar movies",
    version="1.0.0"
)

# CORS middleware - IMPORTANT for frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load model and data - FIXED PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # Go up one level from app/ to project root
model_path = os.path.join(PROJECT_ROOT, 'notebook', 'movie_recommendation_system1.joblib.gz')

print(f"BASE_DIR: {BASE_DIR}")
print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"Looking for model at: {model_path}")
try:
    with gzip.open(model_path, 'rb') as f:
        data = joblib.load(f)
    vectorizer = data['vectorizer']
    new_df = pd.DataFrame(data['dataframe'])  # Reconstruct dataframe from dict
    similarity = data['similarity_matrix']
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    # Initialize empty variables to avoid errors
    vectorizer = None
    new_df = pd.DataFrame()
    similarity = None

# Pydantic model for API validation
class MovieRequest(BaseModel):
    movie: str

    # Example values for API documentation
    class Config:
        schema_extra = {
            "example": {
                "movie": "The Dark Knight"
            }
        }

# Recommendation function
def recommend(movie: str):
    if movie not in new_df['title'].values:
        return []

    movie_index = new_df[new_df['title'] == movie].index[0]
    distance = similarity[movie_index]
    movies_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]
    recommended = [new_df.iloc[i[0]].title for i in movies_list]
    return recommended

# Main recommendation endpoint
@app.post("/recommend")
async def get_recommendation(movie_request: MovieRequest):
    """
    Get movie recommendations based on a movie title
    
    - **movie**: Name of the movie to get recommendations for
    """
    try:
        # Check if model is loaded
        if new_df.empty or similarity is None:
            return {
                "status": "error",
                "message": "Model not loaded properly. Please check the server."
            }
        
        # Get recommendations
        movies = recommend(movie_request.movie)
        
        if not movies:
            return {
                "status": "error",
                "message": f"Movie '{movie_request.movie}' not found in database."
            }
        
        return {
            "status": "success",
            "recommended_movies": movies,
            "input_movie": movie_request.movie
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Recommendation failed: {str(e)}"
        }

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Movie Recommendation API is running 🎬🚀"}

@app.get("/health")
async def health_check():
    """Check if API and model are operational"""
    model_status = "loaded" if (not new_df.empty and similarity is not None) else "not loaded"
    return {
        "status": "healthy", 
        "message": "API is operational",
        "model_status": model_status,
        "movies_count": len(new_df) if not new_df.empty else 0
    }

# Get available movies
@app.get("/movies")
async def get_available_movies(limit: int = 50):
    """Get list of available movies in the database"""
    try:
        if new_df.empty:
            return {
                "status": "error",
                "message": "Movie database not loaded"
            }
        
        movies_list = new_df['title'].tolist()[:limit]
        return {
            "status": "success",
            "movies": movies_list,
            "total_movies": len(new_df)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get movies: {str(e)}"
        }

# Search movies
@app.get("/search")
async def search_movies(query: str, limit: int = 10):
    """Search for movies by title"""
    try:
        if new_df.empty:
            return {
                "status": "error",
                "message": "Movie database not loaded"
            }
        
        # Case-insensitive search
        matching_movies = new_df[new_df['title'].str.contains(query, case=False, na=False)]['title'].tolist()[:limit]
        
        return {
            "status": "success",
            "query": query,
            "movies": matching_movies,
            "count": len(matching_movies)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Search failed: {str(e)}"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)