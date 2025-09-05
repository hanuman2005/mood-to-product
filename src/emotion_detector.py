# ============================================================================
# src/emotion_detector.py
# ============================================================================
import cv2
import numpy as np
from PIL import Image
import tempfile
import os
import time

class EmotionDetector:
    """    Emotion detection using DeepFace library with fallback mechanisms."""
    
    def __init__(self):
        self.deepface_available = self._check_deepface()
    
    def _check_deepface(self):
        """Check if DeepFace is available and working."""
        try:
            from deepface import DeepFace
            return True
        except ImportError:
            print("DeepFace not available. Using fallback emotion detection.")
            return False
        except Exception as e:
            print(f"Error initializing DeepFace: {e}")
            return False
    
    def detect_emotion(self, image):
        """
        Detect emotion from image using DeepFace or fallback method.
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            dict: {
                'success': bool,
                'emotion': str,
                'confidence': float,
                'all_emotions': dict,
                'error': str (if success=False)
            }
        """
        try:
            if self.deepface_available:
                return self._detect_with_deepface(image)
            else:
                return self._fallback_detection(image)
        except Exception as e:
            return {
                'success': False,
                'emotion': None,
                'confidence': 0.0,
                'all_emotions': {},
                'error': str(e)
            }
    
    def _detect_with_deepface(self, image):
        try:
            from deepface import DeepFace

            # Convert PIL Image to NumPy array
            if isinstance(image, Image.Image):
                image_array = np.array(image)
            else:
                image_array = image

            # Convert RGB to BGR for OpenCV
            if len(image_array.shape) == 3:
                image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image_array

            # Create temp file path manually and close immediately
            tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            tmp_path = tmp_file.name
            tmp_file.close()  # Release file lock

            # Write image to temp path
            cv2.imwrite(tmp_path, image_bgr)

            try:
                result = DeepFace.analyze(
                    img_path=tmp_path,
                    actions=['emotion'],
                    enforce_detection=False,
                    detector_backend='opencv'
                )
            finally:
                os.unlink(tmp_path)  # Clean up temp file

            if isinstance(result, list):
                result = result[0]

            emotions = result['emotion']
            dominant_emotion = result['dominant_emotion']
            confidence = emotions[dominant_emotion] / 100.0

            return {
                'success': True,
                'emotion': dominant_emotion,
                'confidence': confidence,
                'all_emotions': {k: v / 100.0 for k, v in emotions.items()},
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'emotion': None,
                'confidence': 0.0,
                'all_emotions': {},
                'error': f"DeepFace error: {str(e)}"
            }

        """Detect emotion using DeepFace library."""
        try:
            from deepface import DeepFace
            
            # Convert PIL Image to numpy array if needed
            if isinstance(image, Image.Image):
                image_array = np.array(image)
            else:
                image_array = image
            
            # Save image temporarily for DeepFace
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                if len(image_array.shape) == 3:
                    # RGB to BGR for OpenCV
                    image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                else:
                    image_bgr = image_array
                
                cv2.imwrite(tmp.name, image_bgr)
                
                # Analyze emotion
                result = DeepFace.analyze(
                    img_path=tmp.name,
                    actions=['emotion'],
                    enforce_detection=False,
                    detector_backend='opencv'
                )
                
                # Clean up temp file
                os.unlink(tmp.name)
                
                # Extract results
                if isinstance(result, list):
                    result = result[0]
                
                emotions = result['emotion']
                dominant_emotion = result['dominant_emotion']
                confidence = emotions[dominant_emotion] / 100.0
                
                return {
                    'success': True,
                    'emotion': dominant_emotion,
                    'confidence': confidence,
                    'all_emotions': {k: v/100.0 for k, v in emotions.items()},
                    'error': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'emotion': None,
                'confidence': 0.0,
                'all_emotions': {},
                'error': f"DeepFace error: {str(e)}"
            }
    
    def _fallback_detection(self, image):
        """
        Fallback emotion detection using simple heuristics.
        This is a placeholder implementation for demo purposes.
        """
        try:
            # Convert to grayscale for basic analysis
            if isinstance(image, Image.Image):
                gray = np.array(image.convert('L'))
            else:
                if len(image.shape) == 3:
                    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                else:
                    gray = image
            
            # Simple heuristic: use image brightness and contrast
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Map brightness and contrast to emotions (very basic)
            if brightness > 150:
                emotion = 'happy'
                confidence = 0.7
            elif brightness < 80:
                emotion = 'sad'
                confidence = 0.6
            elif contrast > 50:
                emotion = 'surprise'
                confidence = 0.5
            else:
                emotion = 'neutral'
                confidence = 0.8
            
            # Create mock emotion distribution
            emotions = ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral']
            all_emotions = {e: 0.1 for e in emotions}
            all_emotions[emotion] = confidence
            
            return {
                'success': True,
                'emotion': emotion,
                'confidence': confidence,
                'all_emotions': all_emotions,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'emotion': None,
                'confidence': 0.0,
                'all_emotions': {},
                'error': f"Fallback detection error: {str(e)}"
            }
    
    def get_available_emotions(self):
        """Get list of available emotions."""
        if self.deepface_available:
            return ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        else:
            return ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral']