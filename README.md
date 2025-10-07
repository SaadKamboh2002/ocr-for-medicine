* the test-docs folder contains some sample images and pdfs to test the ocr
* ocr.py implements only tesseract ocr on images
* pdf_ocr.py implements ocr on pdf as well as images (its implemented in the ocr-only endpoint)
* save-to-db.py is not finalized yet
* ocr-api.py contains two endpoints (extract-medicines and ocr-only)
* ocr-only-api.py contains only the ocr-only endpoint which performs ocr on image or pdf
* meds.py was the early script used to get medicine names from the extracted ocr text using gpt (its now implemented inside the extract-medicines endpoint)
* mongodb-commands.md contains pymongo commands for learning purposes
