# 🔍 AI-Powered Job Listing Extractor (LinkedIn Scraper)

This project uses **LLMs + browser automation** to extract **real-time job listings from LinkedIn**, tailored to job titles intelligently pulled from a resume.

## 💡 What It Does

- Reads a candidate’s resume (PDF)
- Uses a Gemini LLM to extract structured info, especially **suggested job titles**
- Automates a Chrome browser to:
  - Search for jobs on LinkedIn
  - Open job listings
  - Scroll, scrape, and extract structured job data (Job ID, Title, Company, etc.)
- Optionally converts raw scraped job data into clean JSON using Gemini again

## 🔧 Stack

- **Python**
- **LangChain** for LLM interaction (Gemini 2.0 Flash)
- **Google Generative AI SDK**
- **Playwright-based browser automation**
- **Pydantic** and **dotenv** for config
- **PDF parsing and cleaning** for resume processing

## 📂 Project Structure

```
project/
│
├── resume_processor.py          # Logic to extract structured info from PDF resume
├── browser_use/                 # Browser automation code
│   ├── agent/
│   ├── browser/
│   └── ...
├── job_processor.py             # Main execution script
├── .env                         # Store your GEMINI_API_KEY here
└── README.md                    # You're reading it now
```

## 🚀 How To Run

### 1. Requirements

- Python 3.8+
- Google Chrome installed (needs to open in debug mode)

### 2. Setup

```bash
git clone <your-repo-url>
cd <project-dir>
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Add your Gemini API key to `.env`:

```env
GEMINI_API_KEY=your_google_genai_api_key
```

### 3. Run

Make sure Chrome is closed before running (it will be launched in debug mode):

```bash
python job_processor.py
```

### 4. Input

Place your resume PDF (e.g. `Resume_Gopinath_Sharma_Golang.pdf`) in the project folder.

The LLM will extract job titles from it and use them for job search.

## 📌 Notes

- Only scrapes **1 job listing** per run for now (to avoid rate-limiting/spam).
- You can expand to scrape multiple listings by tweaking the loop limit in the task.
- Uses **Gemini LLM twice**:
  1. To extract job titles from resume
  2. To format the scraped job info into valid JSON

## 🔮 Future Ideas

- Auto-apply to jobs using autofill
- Use RAG to match job listings to resume experience
- Build a local cache for scraped jobs to avoid reprocessing
- Export to Airtable / Notion / Google Sheets