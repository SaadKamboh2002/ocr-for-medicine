from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from openai import OpenAI
from pdf_ocr import read_image_and_extract_text, get_file_type
from dotenv import load_dotenv
import os
import tempfile
import shutil
import json
from typing import List, Dict

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Medicine OCR API", description="API for extracting medicine information from images")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/extract-medicines/", response_model=Dict)
async def extract_medicines_from_image(file: UploadFile = File(...)):
    """
    Upload an image or PDF and extract medicine names and dosages using OCR + GPT
    """
    
    # Debug: Print file information
    print(f"Received file: {file.filename}")
    print(f"Content type: {file.content_type}")
    print(f"File size: {file.size if hasattr(file, 'size') else 'Unknown'}")
    
    # Validate file exists
    if not file or not file.filename:
        raise HTTPException(status_code=422, detail="No file provided")
    
    # Validate file type - check both content_type and file extension for images and PDFs
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.pdf']
    allowed_content_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp', 'application/pdf']
    
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
        print("Starting file processing...")
        
        # Determine file type and set appropriate extension
        file_type = get_file_type(file.filename)
        print(f"File type detected: {file_type}")
        
        if file_type == 'pdf':
            suffix = ".pdf"
        else:
            suffix = ".jpg"
        
        print(f"Creating temporary file with suffix: {suffix}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            # Copy uploaded file content to temporary file
            shutil.copyfileobj(file.file, temp_file)
        
        print(f"Temporary file created: {temp_file_path}")
        
        # Extract text using the unified function that handles both images and PDFs
        print("Starting text extraction...")
        ocr_tokens = read_image_and_extract_text(temp_file_path)
        print(f"Extracted {len(ocr_tokens) if ocr_tokens else 0} tokens")
        
        if not ocr_tokens:
            return {
                "success": False,
                "message": "No text detected in the file",
                "ocr_tokens": [],
                "medicines": [],
                "file_type": file_type
            }
        
        # Create prompt for GPT
        prompt = f"""
        List only the names of medicines from this list and perform fuzzy search if you have to: {ocr_tokens}
        Return only the words that are actual medicines in a Python list of strings.
        Also give their dosages if mentioned.
        
        Please respond in the following JSON format:
        {{
            "medicines": [
                {{
                    "name": "medicine_name",
                    "dosage": "dosage_if_mentioned"
                }}
            ]
        }}
        """
        
        # Call OpenAI API
        print("Calling OpenAI API...")
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are an expert pharmacist. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            print("OpenAI API call successful")
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
        
        # Parse GPT response
        gpt_response_text = response.choices[0].message.content
        print(f"GPT response received: {len(gpt_response_text)} characters")
        
        # Parse the JSON string into a Python object
        try:
            gpt_response_json = json.loads(gpt_response_text)
            medicines_list = gpt_response_json.get("medicines", [])
        except json.JSONDecodeError as e:
            print(f"Error parsing GPT response: {e}")
            print(f"Raw response: {gpt_response_text}")
            # Fallback to raw response if parsing fails
            gpt_response_json = {"error": "Failed to parse GPT response", "raw_response": gpt_response_text}
            medicines_list = []
        
        return {
            "success": True,
            "message": "Medicines extracted successfully",
            "ocr_tokens": ocr_tokens,
            "medicines": medicines_list,
            "gpt_response": gpt_response_json,
            "filename": file.filename,
            "file_type": file_type
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like OpenAI API errors)
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            print(f"Cleaning up temporary file: {temp_file_path}")
            os.unlink(temp_file_path)

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
        "message": "Medicine OCR API is running - Supports Images and PDFs with selectable text as well as scanned documents",
        "supported_formats": {
            "images": ["JPG", "JPEG", "PNG", "GIF", "BMP", "TIFF", "WEBP"],
            "documents": ["PDF"]
        },
        "endpoints": {
            "ocr_extraction": "/ocr-only/",
            "extract_medicines": "/extract-medicines/",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)