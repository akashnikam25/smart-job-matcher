# ats_resume_analyzer.py

import PyPDF2
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Load necessary NLTK data files
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

nltk.data.path.append('/custom/path/to/nltk_data')

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def analyze_keywords(resume_text, job_description):
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    resume_tokens = [word for word in word_tokenize(resume_text.lower()) if word.isalpha() and word not in stop_words]
    job_tokens = [word for word in word_tokenize(job_description.lower()) if word.isalpha() and word not in stop_words]
    
    # Extract keywords
    resume_keywords = set(resume_tokens)
    job_keywords = set(job_tokens)
    
    # Calculate keyword match percentage
    matches = resume_keywords.intersection(job_keywords)
    match_percentage = len(matches) / len(job_keywords) * 100 if job_keywords else 0
    return match_percentage

def check_formatting(resume_text):
    # Simple checks for ATS-friendly formatting
    if 'table' in resume_text.lower() or 'image' in resume_text.lower():
        return False
    return True

def calculate_ats_score(resume_text, job_description):
    keyword_score = analyze_keywords(resume_text, job_description)
    format_score = 100 if check_formatting(resume_text) else 0
    
    # Weighted score calculation
    ats_score = (0.7 * keyword_score) + (0.3 * format_score)
    return ats_score

# Example usage
resume_path = 'Resume_Gopinath_ Sharma_Golang.pdf'
job_description = '''About the job


 Minimum Qualifications: 

 2+ years of software development experience 
 Knows Go and Python 
 Familiar with Docker, Kubernetes on cloud platforms (AWS, Azure) 
 Familiar with Linux 

 Preferred Qualifications  : 

 DevOps – Jenkins, ArgoCD, Build pipelines 
 Familiarization with containerization and related technologies such as Docker, Kubernetes, EKS, ECS 

'''

resume_text = extract_text_from_pdf(resume_path)
ats_score = calculate_ats_score(resume_text, job_description)

print(f"ATS Selection Probability: {ats_score:.2f}%") 