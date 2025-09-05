# ============================================================================
# app.py - Main Streamlit Application
# ============================================================================
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Import custom modules
from src.emotion_detector import EmotionDetector
from src.recommender import ProductRecommender
from src.utils import log_feedback, create_feedback_csv, load_image_safely
from src.integrations.spotify_utils import get_playlists_by_mood, is_spotify_available

# Page configuration
st.set_page_config(
    page_title="Mood-to-Product",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .emotion-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .product-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .playlist-card {
        background: linear-gradient(135deg, #1db954 0%, #191414 100%);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
        transition: transform 0.2s;
    }
    .playlist-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(29, 185, 84, 0.3);
    }
    .playlist-image {
        border-radius: 8px;
        width: 80px;
        height: 80px;
        object-fit: cover;
    }
    .spotify-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid #1db954;
    }
    .feedback-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 2rem;
    }
    .section-divider {
        height: 3px;
        background: linear-gradient(90deg, #1db954, #1f77b4);
        border: none;
        border-radius: 2px;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

def display_playlists(playlists, emotion):
    """Display Spotify playlists in a nice format."""
    if not playlists:
        st.warning("No playlists found for this mood. Try a different image!")
        return
    
    st.markdown(f"### 🎵 Playlists for your **{emotion.title()}** mood")
    
    for i, playlist in enumerate(playlists, 1):
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if playlist.get('image'):
                st.image(
                    playlist['image'], 
                    width=80,
                    caption=f"#{i}"
                )
            else:
                st.markdown(f"""
                <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #1db954, #191414); 
                           border-radius: 8px; display: flex; align-items: center; justify-content: center; 
                           color: white; font-size: 24px;">
                    🎵
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="playlist-card">
                <h4 style="margin: 0 0 0.5rem 0;">{playlist['name']}</h4>
                <p style="margin: 0 0 0.5rem 0; opacity: 0.8;">
                    👤 {playlist.get('owner', 'Unknown')} • 
                    🎵 {playlist.get('total_tracks', 0)} tracks
                </p>
                <a href="{playlist['url']}" target="_blank" 
                   style="color: #1db954; text-decoration: none; font-weight: bold;">
                    ▶️ Listen on Spotify
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")

def main():
    # Initialize session state
    if 'detector' not in st.session_state:
        st.session_state.detector = EmotionDetector()
    if 'recommender' not in st.session_state:
        st.session_state.recommender = ProductRecommender()
    if 'analyzed_emotion' not in st.session_state:
        st.session_state.analyzed_emotion = None
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    if 'playlists' not in st.session_state:
        st.session_state.playlists = None
    
    # Create feedback CSV if it doesn't exist
    create_feedback_csv()
    
    # Main header
    st.markdown('<h1 class="main-header">😊 Mood-to-Product Recommender</h1>', 
                unsafe_allow_html=True)
    st.markdown("Upload your photo and discover products & music that match your mood!")
    
    # Check Spotify availability
    spotify_available = is_spotify_available()
    if not spotify_available:
        st.warning("⚠️ Spotify integration not available. Please check your .env file for SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Analytics")
        
        # Show emotion distribution if feedback exists
        if os.path.exists('data/feedback.csv'):
            try:
                feedback_df = pd.read_csv('data/feedback.csv')
                if not feedback_df.empty and 'detected_emotion' in feedback_df.columns:
                    emotion_counts = feedback_df['detected_emotion'].value_counts()
                    fig = px.pie(values=emotion_counts.values, 
                               names=emotion_counts.index,
                               title="Emotion Distribution")
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.write("No analytics available yet")
        
        st.header("ℹ️ About")
        st.write("This app uses AI to detect your emotion from photos and recommends products & music that match your mood.")
        
        st.header("🔧 Settings")
        confidence_threshold = st.slider("Detection Confidence", 0.1, 1.0, 0.6, 0.1)
        
        if spotify_available:
            st.success("🎵 Spotify integration active")
        
        st.header("🎵 Features")
        st.write("• Emotion detection from photos")
        st.write("• Product recommendations")
        if spotify_available:
            st.write("• Spotify playlist suggestions")
        st.write("• User feedback analytics")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📷 Upload Your Photo")
        uploaded_file = st.file_uploader(
            "Choose an image...", 
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear photo of your face for best results"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = load_image_safely(uploaded_file)
            if image is not None:
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                # Analyze emotion
                if st.button("🔍 Analyze Emotion", type="primary"):
                    with st.spinner("Analyzing your emotion..."):
                        try:
                            result = st.session_state.detector.detect_emotion(image)
                            st.session_state.analyzed_emotion = result
                            
                            if result and result['success']:
                                emotion = result['emotion']
                                confidence = result['confidence']
                                
                                # Display emotion result
                                st.markdown(f"""
                                <div class="emotion-card">
                                    <h3>Detected Emotion: {emotion.title()}</h3>
                                    <p>Confidence: {confidence:.2%}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Get recommendations and playlists
                                if confidence >= confidence_threshold:
                                    # Get product recommendations
                                    recommendations = st.session_state.recommender.get_recommendations(
                                        emotion, n_recommendations=5
                                    )
                                    st.session_state.recommendations = recommendations
                                    
                                    # Get Spotify playlists
                                    if spotify_available:
                                        with st.spinner("Finding matching playlists..."):
                                            try:
                                                playlists = get_playlists_by_mood(emotion, n_playlists=5)
                                                st.session_state.playlists = playlists
                                            except Exception as e:
                                                st.error(f"Error getting playlists: {str(e)}")
                                                st.session_state.playlists = []
                                else:
                                    st.warning(f"Low confidence ({confidence:.2%}). Try a clearer image.")
                            else:
                                st.error(f"Could not detect emotion: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Error analyzing emotion: {str(e)}")
    
    with col2:
        st.header("🛍️ Recommended Products")
        
        if st.session_state.recommendations is not None and not st.session_state.recommendations.empty:
            # Display recommendations
            for idx, product in st.session_state.recommendations.iterrows():
                with st.container():
                    col_img, col_info = st.columns([1, 2])
                    
                    with col_img:
                        if pd.notna(product['image_url']) and product['image_url'].startswith('http'):
                            try:
                                st.image(product['image_url'], width=100)
                            except:
                                st.write("🖼️ Image not available")
                        else:
                            st.write("🖼️ No image")
                    
                    with col_info:
                        st.markdown(f"""
                        <div class="product-card">
                            <h4>{product['name']}</h4>
                            <p><strong>Price:</strong> ${product['price']:.2f}</p>
                            <p><strong>Mood Tags:</strong> {product['mood_tags']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
        
        elif st.session_state.analyzed_emotion is not None:
            if st.session_state.analyzed_emotion.get('success'):
                st.info("Upload an image and analyze your emotion to see product recommendations!")
            else:
                st.warning("No recommendations available. Try uploading a different image.")
        else:
            st.info("Upload an image and click 'Analyze Emotion' to get started!")
    
    # Spotify Playlists Section (Full Width)
    if st.session_state.playlists is not None and spotify_available:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        
        with st.container():
            st.markdown("""
            <div class="spotify-section">
                <h2 style="color: #1db954; margin-bottom: 1rem;">
                    🎵 Spotify Playlists for Your Mood
                </h2>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.analyzed_emotion and st.session_state.analyzed_emotion.get('success'):
                emotion = st.session_state.analyzed_emotion['emotion']
                display_playlists(st.session_state.playlists, emotion)
    
    # Feedback Section
    if (st.session_state.recommendations is not None and 
        not st.session_state.recommendations.empty and 
        st.session_state.analyzed_emotion is not None):
        
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
            st.subheader("💭 How did we do?")
            
            col_feedback1, col_feedback2 = st.columns(2)
            
            with col_feedback1:
                rating = st.selectbox(
                    "Rate our recommendations:",
                    [1, 2, 3, 4, 5],
                    index=4,
                    format_func=lambda x: "⭐" * x
                )
            
            with col_feedback2:
                feedback_text = st.text_area("Additional feedback (optional):")
            
            if st.button("Submit Feedback", type="primary"):
                if st.session_state.analyzed_emotion:
                    log_feedback(
                        emotion=st.session_state.analyzed_emotion['emotion'],
                        confidence=st.session_state.analyzed_emotion['confidence'],
                        rating=rating,
                        feedback_text=feedback_text,
                        num_recommendations=len(st.session_state.recommendations)
                    )
                    st.success("Thank you for your feedback! 🙏")
                    st.balloons()
                else:
                    st.error("No emotion analysis found. Please analyze an image first.")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: gray;'>Made with ❤️ using Streamlit, DeepFace & Spotify API</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()