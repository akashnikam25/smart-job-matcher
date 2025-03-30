import PyPDF2
import sys
import re
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

def extract_text_from_pdf(pdf_path):
    """Extract text from each page of the PDF and return a list of (page_number, text)."""
    pages = []
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                pages.append((i + 1, page_text.strip()))
    return pages

def clean_text(text):
    """Remove extra spaces and format the text for better readability."""
    # Remove extra spaces between characters
    text = ' '.join(text.split())
    
    # Add new lines after section headers
    headers = ["SUMMARY", "PROJECTS", "EDUCATION", "STRENGTHS", "SKILLS"]
    for header in headers:
        text = text.replace(header, f"\n{header}\n")

    # Add bullet points for lists
    text = text.replace("-", "\n- ")

    # Remove spaces within words that are meant to be bold or emphasized
    text = re.sub(r'(?<=\b\w)\s(?=\w\b)', '', text)

    # Correct specific technology names
    text = text.replace('Next . js', 'Next.js')
    text = text.replace('React . js', 'React.js')

    return text

def print_structured_pdf_content(pdf_path):
    """Print PDF content with headers for each page."""
    pages = extract_text_from_pdf(pdf_path)
    if pages:
        for page_number, text in pages:
            # Clean and format the text before printing
            formatted_text = clean_text(text)
            print(formatted_text)
            print("\n")
    else:
        print("No text found in the PDF.")

def extract_structured_info_from_text(text):
    api_key = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""
    Here's a resume in raw text format:
    ---
    {text}
    ---
    Extract the following information as valid JSON without any markdown formatting or additional text:
    - Name
    - Email
    - Phone
    - Summary
    - Projects (each with name, tech stack, and description)
    - Education
    - Strengths
    - Skills
    - Suggested Job Titles based on the skills, projects, and experience

    Please ensure that all technology names and terms are correctly formatted. For example:
    - 'Next . js' should be 'Next.js'
    - 'React . js' should be 'React.js'
    - Correct any similar formatting errors you find.

    Guidelines:
    - Provide the output strictly as valid JSON.
    - Do NOT include markdown (```json``` or similar tags) in the output.
    """

    response = model.generate_content(prompt)
    return response.text

def get_job_titles_from_resume(pdf_path):
    pages = extract_text_from_pdf(pdf_path)
    full_text = "\n".join([clean_text(text) for _, text in pages])
    structured_info = extract_structured_info_from_text(full_text)
    
    # Print the structured_info to debug
    print("Structured Info:", structured_info)
    
    # Check if structured_info is empty
    if not structured_info:
        print("Error: No structured information returned from the AI model.")
        sys.exit(1)  # Exit the program with an error code
    
    # Check if structured_info is valid JSON
    try:
        resume_data = json.loads(structured_info)
        return resume_data.get("Suggested Job Titles", [])
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        sys.exit(1)  # Exit the program with an error code

def main():
    if len(sys.argv) < 2:
        print("Usage: python resume_processor.py <pdf_file_path>")
        sys.exit(1)

    pdf_file_path = sys.argv[1]

    try:
        pages = extract_text_from_pdf(pdf_file_path)
        full_text = "\n".join([clean_text(text) for _, text in pages])

        structured_info = extract_structured_info_from_text(full_text)
        print("\nStructured Resume Info:\n", structured_info)

    except FileNotFoundError:
        print(f"Error: The file '{pdf_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()