from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from openai import OpenAI
from pdf_ocr import read_image_and_extract_text, get_file_type
import os
import tempfile
import shutil
import json
from typing import List, Dict


# Initialize FastAPI app
app = FastAPI(title="OCR Only API", description="API for extracting text from images")
    

@app.post("/ocr-only/", response_model=Dict)
async def ocr_only(file: UploadFile = File(...)):
    """
    Upload an image or PDF and extract text using OCR (without GPT processing)
    """
    
    # Debug: Print file information
    print(f"OCR-Only - Received file: {file.filename}")
    print(f"OCR-Only - Content type: {file.content_type}")
    
    # Validate file exists
    if not file or not file.filename:
        raise HTTPException(status_code=422, detail="No file provided")
    
    # Validate file type - support both images and PDFs
    allowed_image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp']
    allowed_pdf_extensions = ['.pdf']
    allowed_extensions = allowed_image_extensions + allowed_pdf_extensions
    
    allowed_image_content_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp']
    allowed_pdf_content_types = ['application/pdf']
    allowed_content_types = allowed_image_content_types + allowed_pdf_content_types
    
    file_extension = os.path.splitext(file.filename.lower())[1] if file.filename else ''
    
    # Check if it's a valid file by extension or content type
    is_valid_file = (
        file_extension in allowed_extensions or 
        (file.content_type and file.content_type in allowed_content_types) or
        (file.content_type and file.content_type.startswith('image/')) or
        (file.content_type and file.content_type == 'application/pdf')
    )
    
    if not is_valid_file:
        raise HTTPException(
            status_code=400, 
            detail=f"File must be an image or PDF. Received file: {file.filename}, Content-Type: {file.content_type}"
        )
    
    # Create temporary file to save uploaded file
    temp_file_path = None
    try:
        # Determine file type and set appropriate suffix
        file_type = get_file_type(file.filename)
        file_extension = os.path.splitext(file.filename.lower())[1] if file.filename else '.tmp'
        
        # Create temporary file with correct extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file_path = temp_file.name
            # Copy uploaded file content to temporary file
            shutil.copyfileobj(file.file, temp_file)
        
        # Extract text using OCR (handles both images and PDFs)
        ocr_tokens = read_image_and_extract_text(temp_file_path)
        
        return {
            "success": True,
            "message": f"OCR extraction completed for {file_type}",
            "file_type": file_type,
            "ocr_tokens": ocr_tokens,
            "total_words": len(ocr_tokens),
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        
@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {
        "message": "OCR Only API is running - Supports Images and PDFs with selectable text as well as scanned documents",
        "supported_formats": {
            "images": ["JPG", "JPEG", "PNG", "GIF", "BMP", "TIFF", "WEBP"],
            "documents": ["PDF"]
        },
        "endpoints": {
            "ocr_extraction": "/ocr-only/",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)