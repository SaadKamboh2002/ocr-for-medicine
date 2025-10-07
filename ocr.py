import pytesseract
import cv2

def read_image_and_extract_text(image_path):
    # load image
    image = cv2.imread(image_path)

    # convert to grayscale for better accuracy
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    text = pytesseract.image_to_string(gray)


    # create a list to store individual words
    words_list = []

    # Split the text into words and append each to the list
    if text.strip():  # Check if text is not empty
        words = text.split()
        for word in words:
            # removing any leading/trailing whitespace or newlines
            cleaned_word = word.strip()
            if cleaned_word:  # Only append non-empty words
                words_list.append(cleaned_word)

    print("\nWords extracted to list:")
    print(words_list)
    print(f"\nTotal words detected: {len(words_list)}") # now from these words i will match with my meds list using fuzzymatching

    return words_list


# import easyocr

# Alternative implementation with EasyOCR
# reader = easyocr.Reader(['en'])
# result = reader.readtext('test.jpg')
# words_list_easyocr = []
# 
# for (bbox, text, prob) in result:
#     print(f"Detected text: {text} (Confidence: {prob:.2f})")
#     # Split each detected text block into words and append to list
#     words = text.split()
#     for word in words:
#         cleaned_word = word.strip()
#         if cleaned_word:
#             words_list_easyocr.append(cleaned_word)
# 
# print(f"\nEasyOCR words list: {words_list_easyocr}")
# print(f"Total words with EasyOCR: {len(words_list_easyocr)}")

