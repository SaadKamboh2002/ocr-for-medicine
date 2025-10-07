import pytesseract
import cv2
import fitz  # PyMuPDF
import os
import tempfile
import io
from PIL import Image
import numpy as np

# first check if pdf is text based or scanned image based
def extract_text_from_pdf_pymupdf(pdf_path):

    words_list = []
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            if text.strip():
                words = text.split()
                for word in words:
                    cleaned_word = word.strip()
                    if cleaned_word:
                        words_list.append(cleaned_word)
        
        doc.close()
        print(f"Extracted {len(words_list)} words from PDF using PyMuPDF")
        return words_list
        
    except Exception as e:
        print(f"Error extracting text with PyMuPDF: {str(e)}")
        return []

# if pdf is scanned image based - using PyMuPDF only (no Poppler required)
def extract_text_from_pdf_ocr(pdf_path):
    words_list = []
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            print(f"Processing page {page_num + 1}/{len(doc)}")
            
            # Convert PDF page to image using PyMuPDF
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR quality
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(gray)
            
            if text.strip():
                words = text.split()
                for word in words:
                    cleaned_word = word.strip()
                    if cleaned_word:
                        words_list.append(cleaned_word)
        
        doc.close()
        print(f"Extracted {len(words_list)} words from PDF using OCR")
        return words_list
        
    except Exception as e:
        print(f"Error extracting text with OCR: {str(e)}")
        return []

def read_image_and_extract_text(file_path):
    """
    Enhanced function to extract text from both images and PDFs
    """
    file_extension = os.path.splitext(file_path.lower())[1]
    
    if file_extension == '.pdf':
        return process_pdf_file(file_path)
    else:
        return process_image_file(file_path)

# Process PDF file tries to extract text using pymupdf first, then OCR if needed
def process_pdf_file(pdf_path):
    print(f"Processing PDF: {pdf_path}")
    
    # First try to extract text directly (for text-based PDFs)
    words_list = extract_text_from_pdf_pymupdf(pdf_path)
    
    # If no text found or very few words, try OCR (for scanned PDFs)
    if len(words_list) < 5:
        print("📸 Text extraction yielded few results, trying OCR...")
        ocr_words = extract_text_from_pdf_ocr(pdf_path)
        
        # Use OCR results if they're better
        if len(ocr_words) > len(words_list):
            words_list = ocr_words
    
    print(f"\nWords extracted from PDF:")
    print(words_list)
    print(f"\nTotal words detected: {len(words_list)}")
    
    return words_list

# if simple image like jpg, png etc then perform ocr directly
def process_image_file(image_path):

    print(f"Processing Image: {image_path}")
    
    # Load image
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return []
    
    # Convert to grayscale for better accuracy
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    text = pytesseract.image_to_string(gray)
    
    # Create a list to store individual words
    words_list = []
    
    # Split the text into words and append each to the list
    if text.strip():  # Check if text is not empty
        words = text.split()
        for word in words:
            # Removing any leading/trailing whitespace or newlines
            cleaned_word = word.strip()
            if cleaned_word:  # Only append non-empty words
                words_list.append(cleaned_word)
    
    print(f"\nWords extracted from image:")
    print(words_list)
    print(f"\nTotal words detected: {len(words_list)}")
    
    return words_list

def get_file_type(file_path):
    """
    Determine if file is PDF or image
    """
    file_extension = os.path.splitext(file_path.lower())[1]
    
    if file_extension == '.pdf':
        return 'pdf'
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp']:
        return 'image'
    else:
        return 'unknown'

# Test function
if __name__ == "__main__":
    test_files = ['doc.pdf'] # add test file here
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n{'='*50}")
            print(f"Testing with {test_file}")
            print('='*50)
            words = read_image_and_extract_text(test_file)
            break
    else:
        print("No test files found!")