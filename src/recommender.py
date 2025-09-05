import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO)

class ProductRecommender:
    def __init__(self, products_csv_path='data/products.csv'):
        self.products_csv_path = products_csv_path
        self.products_df = None
        self.emotion_mapping = self._create_emotion_mapping()
        self.load_products()

    def _create_emotion_mapping(self):
        return {
            'happy': ['entertainment', 'social', 'celebration', 'joy', 'fun', 'colorful'],
            'sad': ['comfort', 'cozy', 'self-care', 'healing', 'soft', 'warm'],
            'angry': ['stress-relief', 'physical', 'intense', 'powerful', 'bold'],
            'surprise': ['unique', 'innovative', 'exciting', 'novel', 'creative'],
            'fear': ['safety', 'security', 'protective', 'calming', 'reassuring'],
            'disgust': ['cleansing', 'fresh', 'pure', 'minimal', 'detox'],
            'neutral': ['practical', 'everyday', 'basic', 'functional', 'versatile']
        }

    def load_products(self):
        try:
            if os.path.exists(self.products_csv_path):
                self.products_df = pd.read_csv(self.products_csv_path)
                logging.info(f"Loaded {len(self.products_df)} products")
            else:
                logging.warning("Products CSV not found. Creating sample data.")
                self._create_sample_products()
        except Exception as e:
            logging.error(f"Error loading products: {e}")
            self._create_sample_products()

    def _create_sample_products(self):
        sample_products = [
            {'product_id': 1, 'name': 'Wireless Bluetooth Headphones', 'price': 99.99,
             'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300',
             'mood_tags': 'entertainment, music, joy, fun'},
            {'product_id': 2, 'name': 'Aromatherapy Essential Oil Set', 'price': 45.50,
             'image_url': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=300',
             'mood_tags': 'comfort, relaxation, healing, calming'},
            # ... (rest of sample products unchanged)
        ]
        self.products_df = pd.DataFrame(sample_products)
        os.makedirs('data', exist_ok=True)
        self.products_df.to_csv(self.products_csv_path, index=False)
        logging.info(f"Created sample products CSV at {self.products_csv_path}")

    def get_recommendations(self, emotion, n_recommendations=5):
        if self.products_df is None or self.products_df.empty:
            return pd.DataFrame()
        emotion = emotion.lower()
        if emotion not in self.emotion_mapping:
            return self.products_df.sample(n=min(n_recommendations, len(self.products_df)))
        emotion_tags = self.emotion_mapping[emotion]
        scores = []
        for _, product in self.products_df.iterrows():
            product_tags = [tag.strip() for tag in str(product['mood_tags']).lower().split(',')]
            intersection = set(emotion_tags) & set(product_tags)
            score = len(intersection) / len(set(emotion_tags) | set(product_tags))
            score += np.random.uniform(-0.1, 0.1)
            scores.append(score)
        products_with_scores = self.products_df.copy()
        products_with_scores['relevance_score'] = scores
        return products_with_scores.sort_values('relevance_score', ascending=False).head(n_recommendations).drop('relevance_score', axis=1)

    def get_product_by_id(self, product_id):
        if self.products_df is None:
            return None
        result = self.products_df[self.products_df['product_id'] == product_id]
        return result.iloc[0] if not result.empty else None

    def add_product(self, product_data):
        if self.products_df is None:
            self.products_df = pd.DataFrame()
        self.products_df = pd.concat([self.products_df, pd.DataFrame([product_data])], ignore_index=True)
        self.products_df.to_csv(self.products_csv_path, index=False)

    def get_all_products(self):
        """Return all products as a DataFrame."""
        return self.products_df

    def search_products(self, query):
        """Search products by name or mood tags."""
        if self.products_df is None:
            return pd.DataFrame()
        query = query.lower()
        mask = (
            self.products_df['name'].str.lower().str.contains(query, na=False) |
            self.products_df['mood_tags'].str.lower().str.contains(query, na=False)
        )
        return self.products_df[mask]
