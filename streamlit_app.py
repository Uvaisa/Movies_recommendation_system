import streamlit as st
import requests
import pandas as pd

# Page configuration - remove sidebar and set layout
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="centered",  # Changed to centered
    initial_sidebar_state="collapsed"  # Collapse sidebar
)

# Hide sidebar completely
st.markdown("""
<style>
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Center the main content */
    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom styling */
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .recommendation-header {
        color: #1f77b4;
        font-size: 1.5rem;
        margin-top: 2rem;
        text-align: center;
    }
    .success-message {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        text-align: center;
    }
    .error-message {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        text-align: center;
    }
    .center-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .movie-item {
        padding: 1rem;
        margin: 0.5rem 0;
        font-size: 1.2rem;
        font-weight: 500;
        color: #1f77b4;
        border-bottom: 2px solid #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_URL = "http://localhost:8000"

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_URL}/health")
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def get_available_movies(limit=100):
    """Get list of available movies from API"""
    try:
        response = requests.get(f"{API_URL}/movies", params={"limit": limit})
        if response.status_code == 200:
            data = response.json()
            return data.get("movies", []) if data.get("status") == "success" else []
        return []
    except:
        return []

def search_movies(query, limit=20):
    """Search movies by title"""
    try:
        response = requests.get(f"{API_URL}/search", params={"query": query, "limit": limit})
        if response.status_code == 200:
            data = response.json()
            return data.get("movies", []) if data.get("status") == "success" else []
        return []
    except:
        return []

def get_recommendations(movie_title):
    """Get movie recommendations from API"""
    try:
        response = requests.post(
            f"{API_URL}/recommend",
            json={"movie": movie_title}
        )
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": "API request failed"}
    except Exception as e:
        return {"status": "error", "message": f"Connection error: {str(e)}"}

def main():
    # Header
    st.markdown('<h1 class="main-header">🎬 Movie Recommendation System</h1>', unsafe_allow_html=True)
    
    # API Health Check - centered
    api_healthy, health_data = check_api_health()
    
    if api_healthy:
        st.success("✅ API is connected and ready!")
    else:
        st.error("❌ API is not connected")
        st.info("Make sure the FastAPI server is running on http://localhost:8000")
        return
    
    
    # Main content - centered
    st.markdown('<div class="center-content">', unsafe_allow_html=True)
    
    # Movie selection section
    st.subheader("🎯 Select a Movie")
    
    movie_options = get_available_movies(200)
    
    if movie_options:
        # Movie dropdown
        selected_movie = st.selectbox(
            "Choose from popular movies:",
            options=movie_options,
            index=0,
            help="Select a movie to get recommendations"
        )
        
        # Manual input
        st.write("**Or enter any movie name:**")
        manual_movie = st.text_input("Type movie title here:", placeholder="e.g., The Dark Knight, Inception...")
        
        # Use manual input if provided, otherwise use dropdown selection
        movie_to_recommend = manual_movie.strip() if manual_movie.strip() else selected_movie
        
        # Get recommendations button - centered
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎭 Get Movie Recommendations", type="primary", use_container_width=True):
                if movie_to_recommend:
                    with st.spinner("Finding similar movies..."):
                        result = get_recommendations(movie_to_recommend)
                    
                    st.markdown("---")
                    
                    if result["status"] == "success":
                        st.markdown(f'<div class="recommendation-header">🎬 Movies similar to "{movie_to_recommend}":</div>', unsafe_allow_html=True)
                        
                        recommendations = result["recommended_movies"]
                        
                        # Display movies without containers - clean and visible
                        for i, movie in enumerate(recommendations, 1):
                            st.markdown(f'<div class="movie-item">#{i} {movie}</div>', unsafe_allow_html=True)
                        
                        st.success(f"✅ Found {len(recommendations)} great recommendations!")
                        
                    else:
                        st.error(f"❌ {result['message']}")
                else:
                    st.warning("⚠️ Please select or enter a movie title")
    
    else:
        st.error("❌ Could not load movie list. Please check API connection.")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🎬 Movie Recommendation System | Built with FastAPI & Streamlit"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()