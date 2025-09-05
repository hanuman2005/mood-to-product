# Mood-to-Product Streamlit Project
# Complete folder structure with all files

# ============================================================================
# README.md
# ============================================================================
"""
# Mood-to-Product Recommendation System

A Streamlit web application that detects user emotions from uploaded images and recommends products based on their detected mood.

## Features

- **Emotion Detection**: Uses DeepFace library to analyze facial emotions from uploaded images
- **Product Recommendations**: Matches detected emotions to relevant products from a curated database
- **Feedback System**: Collects user feedback to improve recommendations
- **Interactive UI**: Clean and intuitive Streamlit interface

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mood-to-product
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
mood-to-product/
├── README.md
├── requirements.txt
├── .gitignore
├── app.py                    # Streamlit app (entrypoint)
├── src/
│   ├── emotion_detector.py   # wraps DeepFace / fallback
│   ├── recommender.py        # loads products.csv -> returns recommendations
│   └── utils.py              # small helpers
├── data/
│   ├── products.csv          # product_id,name,price,image_url,mood_tags
│   └── feedback.csv          # created at runtime (logs)
├── assets/
│   └── products/             # optional local images
├── notebooks/                # quick experiments (optional)
└── Dockerfile                # optional for deployment
```

## Usage

1. Upload an image with a clear face
2. Wait for emotion analysis
3. Browse recommended products based on your detected mood
4. Provide feedback to help improve recommendations

## Technologies Used

- **Streamlit**: Web application framework
- **DeepFace**: Emotion detection
- **Pandas**: Data manipulation
- **Pillow**: Image processing
- **OpenCV**: Computer vision utilities

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License
"""

# mood-to-product
