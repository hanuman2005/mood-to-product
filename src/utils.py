import pandas as pd
import numpy as np
from PIL import Image
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def load_products(path="data/products.csv"):
    if not os.path.exists(path):
        logging.warning(f"Products file not found at {path}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        required_columns = ["product_id", "name", "price", "mood_tags"]
        if not all(col in df.columns for col in required_columns):
            logging.error("Missing required columns in products.csv")
            return pd.DataFrame()
        return df
    except Exception as e:
        logging.error(f"Error loading products: {e}")
        return pd.DataFrame()

def load_image_safely(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image.copy()
    except Exception as e:
        logging.error(f"Error loading image: {e}")
        return None

def create_feedback_csv():
    feedback_path = 'data/feedback.csv'
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(feedback_path):
        columns = ['timestamp', 'detected_emotion', 'confidence', 'rating', 'feedback_text', 'num_recommendations']
        pd.DataFrame(columns=columns).to_csv(feedback_path, index=False)
        logging.info(f"Created feedback CSV at {feedback_path}")

def log_feedback(emotion, confidence, rating, feedback_text="", num_recommendations=0):
    feedback_path = 'data/feedback.csv'
    new_feedback = {
        'timestamp': datetime.now().isoformat(),
        'detected_emotion': emotion,
        'confidence': confidence,
        'rating': rating,
        'feedback_text': feedback_text,
        'num_recommendations': num_recommendations
    }
    try:
        df = pd.read_csv(feedback_path)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([new_feedback])], ignore_index=True)
    df.to_csv(feedback_path, index=False)
    logging.info(f"Logged feedback: {emotion} - Rating: {rating}")

def resize_image(image, max_size=(800, 600)):
    try:
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    except Exception as e:
        logging.error(f"Error resizing image: {e}")
        return image

def format_price(price):
    try:
        return f"${float(price):.2f}"
    except (ValueError, TypeError):
        return "Price not available"

def clean_mood_tags(tags):
    try:
        if pd.isna(tags):
            return "No tags available"
        tag_list = [tag.strip().title() for tag in str(tags).split(',')]
        return ', '.join(tag_list)
    except Exception:
        return "No tags available"

def calculate_emotion_confidence_level(confidence):
    if confidence >= 0.9: return "Very High"
    elif confidence >= 0.7: return "High"
    elif confidence >= 0.5: return "Medium"
    elif confidence >= 0.3: return "Low"
    else: return "Very Low"

def get_emotion_emoji(emotion):
    return {
        'happy': '😊', 'sad': '😢', 'angry': '😠',
        'surprise': '😲', 'fear': '😨', 'disgust': '🤢', 'neutral': '😐'
    }.get(emotion.lower(), '🤔')

def validate_product_data(product_data):
    required_fields = ['product_id', 'name', 'price', 'mood_tags']
    for field in required_fields:
        if field not in product_data:
            return False, f"Missing required field: {field}"
    try:
        float(product_data['price'])
        int(product_data['product_id'])
    except (ValueError, TypeError):
        return False, "Invalid format in price or product_id"
    return True, "Valid"

def export_feedback_summary():
    feedback_path = 'data/feedback.csv'
    if not os.path.exists(feedback_path): return None
    try:
        df = pd.read_csv(feedback_path)
        if df.empty: return None
        return {
            'total_feedback': len(df),
            'average_rating': df['rating'].mean(),
            'emotion_distribution': df['detected_emotion'].value_counts().to_dict(),
            'confidence_stats': {
                'mean': df['confidence'].mean(),
                'min': df['confidence'].min(),
                'max': df['confidence'].max()
            }
        }
    except Exception as e:
        logging.error(f"Error generating feedback summary: {e}")
        return None
