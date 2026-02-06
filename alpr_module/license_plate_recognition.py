"""
License Plate Recognition (LPR) Module using EasyOCR
AutoFINE System
"""

import cv2
import numpy as np
import easyocr
import re
from PIL import Image
import os

# Initialize EasyOCR reader (lazy loading)
_reader = None

def get_reader():
    """Initialize and return EasyOCR reader (singleton pattern)"""
    global _reader
    if _reader is None:
        # Initialize EasyOCR reader for English
        # Set gpu=False if CUDA is not available
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader

def preprocess_image(image_path):
    """Preprocess image for better OCR results"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image from {image_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply denoising
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    return img, gray, enhanced, thresh

def detect_license_plate_region(image):
    """Detect potential license plate regions in the image"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Morphological operations to connect edges
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
    morph = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by aspect ratio and area (license plates are typically rectangular)
    plate_regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h) if h > 0 else 0
        area = cv2.contourArea(contour)
        
        # Typical license plate aspect ratio: 2.0 to 5.0
        if 2.0 <= aspect_ratio <= 5.0 and area > 1000:
            plate_regions.append((x, y, w, h))
    
    return plate_regions

def clean_license_plate_text(text):
    """Clean and format recognized license plate text"""
    if not text:
        return None
    
    # Remove special characters, keep only alphanumeric
    cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
    
    # Remove common OCR errors
    # Replace similar looking characters
    replacements = {
        '0': 'O',  # Can be context-dependent
        '1': 'I',
        '5': 'S',
        '8': 'B'
    }
    
    # Apply replacements only in certain positions
    # (This is a simplified version, can be improved with ML)
    
    # Filter out very short strings (likely noise)
    if len(cleaned) < 3:
        return None
    
    return cleaned

def recognize_license_plate(image_path, use_region_detection=True):
    """
    Main function to recognize license plate from image
    
    Args:
        image_path: Path to the image file
        use_region_detection: Whether to use region detection before OCR
    
    Returns:
        tuple: (license_plate_text, confidence_score)
    """
    try:
        reader = get_reader()
        
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return None, 0.0
        
        license_plate = None
        max_confidence = 0.0
        
        if use_region_detection:
            # Try to detect license plate regions first
            plate_regions = detect_license_plate_region(img)
            
            if plate_regions:
                # Process each detected region
                for x, y, w, h in plate_regions:
                    # Extract region
                    roi = img[y:y+h, x:x+w]
                    
                    # Preprocess ROI
                    _, _, enhanced, _ = preprocess_image_roi(roi)
                    
                    # Perform OCR on region
                    results = reader.readtext(enhanced)
                    
                    for (bbox, text, conf) in results:
                        cleaned_text = clean_license_plate_text(text)
                        if cleaned_text and conf > max_confidence:
                            license_plate = cleaned_text
                            max_confidence = conf
        else:
            # Direct OCR on entire image
            results = reader.readtext(img)
            
            for (bbox, text, conf) in results:
                cleaned_text = clean_license_plate_text(text)
                if cleaned_text and conf > max_confidence:
                    license_plate = cleaned_text
                    max_confidence = conf
        
        # If region detection failed, try full image OCR
        if not license_plate:
            preprocessed_images = preprocess_image(image_path)
            for processed_img in preprocessed_images[1:]:  # Skip original
                results = reader.readtext(processed_img)
                for (bbox, text, conf) in results:
                    cleaned_text = clean_license_plate_text(text)
                    if cleaned_text and conf > max_confidence:
                        license_plate = cleaned_text
                        max_confidence = conf
        
        return license_plate, max_confidence
    
    except Exception as e:
        print(f"Error in license plate recognition: {str(e)}")
        return None, 0.0

def preprocess_image_roi(roi):
    """Preprocess a region of interest (ROI)"""
    if len(roi.shape) == 3:
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    else:
        gray = roi
    
    # Resize if too small
    h, w = gray.shape
    if h < 30 or w < 100:
        scale = max(30/h, 100/w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    return gray, denoised, enhanced

def batch_process_images(image_paths):
    """Process multiple images in batch"""
    results = []
    for image_path in image_paths:
        plate, confidence = recognize_license_plate(image_path)
        results.append({
            'image_path': image_path,
            'license_plate': plate,
            'confidence': confidence
        })
    return results

# Test function
if __name__ == '__main__':
    # Example usage
    test_image = 'test_plate.jpg'
    if os.path.exists(test_image):
        plate, conf = recognize_license_plate(test_image)
        print(f"License Plate: {plate}, Confidence: {conf:.2%}")
