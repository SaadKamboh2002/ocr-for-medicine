
from openai import OpenAI
from pdf_ocr import read_image_and_extract_text
from dotenv import load_dotenv
import os

load_dotenv()
# extract medicine names from images nby giving the raw text to llm
def extract_medicines_from_image(image_path: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    ocr_tokens = read_image_and_extract_text(image_path)

    prompt = f"""
    list only the names of medicine from this list and perform fuzzy search if you have to {ocr_tokens}
    Return only the words that are actual medicines in a Python list of strings.
    also give their dosages if mentioned. 
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are an expert pharmacist."},
            {"role": "user", "content": prompt}
        ],
    )

    # Extract GPT output
    medicines_found = response.choices[0].message.content
    print(medicines_found)
    return medicines_found

if __name__ == "__main__":
    meds = extract_medicines_from_image("test-docs/sindh-scanned-list.pdf")
    print("Extracted Medicines:", meds)
