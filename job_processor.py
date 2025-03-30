import json
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Controller
from pydantic import SecretStr
import os
from dotenv import load_dotenv
import asyncio
from resume_processor import extract_structured_info_from_text, extract_text_from_pdf, clean_text
import sys

from browser_use.agent.views import ActionResult
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext
import google.generativeai as genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

browser = Browser(
	config=BrowserConfig(
		# NOTE: you need to close your chrome browser - so that this can open your browser in debug mode
		chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        
	)
)



# Initialize the model
llm = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash-exp', 
    api_key=SecretStr(api_key)
)

controller = Controller()

# Function to get job titles from resume
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
    
    try:
        # 1. Remove markdown code block syntax
        structured_info = structured_info.replace("```json", "").replace("```", "").strip()
        
        # 2. Find and extract the JSON object
        import re
        json_match = re.search(r'(\{.*\})', structured_info, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in the response.")
        
        json_content = json_match.group(1)
        
        # 3. Fix common JSON formatting issues
        # Remove any invalid line breaks inside strings
        json_content = re.sub(r'("\s*:\s*".*?)\n(.*?")', r'\1 \2', json_content)
        
        # 4. Parse the JSON
        resume_data = json.loads(json_content)
        
        # 5. Try different possible key names for job titles
        possible_keys = ["suggested_job_titles", "Suggested_Job_Titles", "Suggested Job Titles", 
                          "suggested job titles", "job_titles", "Job Titles"]
        
        for key in possible_keys:
            if key in resume_data:
                return resume_data[key]
        
        # If no matching key is found
        print(f"Warning: No job titles found in the data. Available keys: {list(resume_data.keys())}")
        return []
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error processing JSON: {e}")
        
        # Additional debugging - print part of the problematic JSON
        if 'json_content' in locals():
            print("JSON Content (first 200 chars):", json_content[:200])
            
        # Attempt to identify specific JSON issues
        if isinstance(e, json.JSONDecodeError):
            line_no = e.lineno
            col_no = e.colno
            print(f"JSON error at line {line_no}, column {col_no}")
            
            # Try to get the problematic line
            if 'json_content' in locals():
                lines = json_content.split('\n')
                if 0 <= line_no - 1 < len(lines):
                    print(f"Problematic line: {lines[line_no - 1]}")
                    print(f"Position: {' ' * (col_no - 1)}^")
        
        sys.exit(1)  # Exit the program with an error code

# Get job titles from the resume
job_titles = get_job_titles_from_resume('Resume_Gopinath_ Sharma_Golang.pdf')

# Print all job titles
print("Extracted Job Titles:", job_titles)

# Ensure there is at least one job title
if not job_titles:
    print("No job titles found. Exiting.")
    sys.exit(1)

# Create a task for the first job title only
first_job_title = job_titles[0]
task_description = f"""
1. Enter Job Search Criteria (Only Once)
   - In the "Title, skills, or company" field, enter: {first_job_title}.
   - In the "City, state, or zip code" field, enter: Pune, Maharashtra, India.
   - Press Enter to search.

2. Extract Job Listings (Only Once)
   - Wait for the job listings to load.

3. Iterate Through Selected Jobs
   - For each job, open the job details.
   - Scroll down 2000 pixels to extract the following fields explicitly:
     - Job ID 
     - Job Title
     - Company Name
     - Location
     - Job Description
     - Posting Date
     - Job URL (application link)

   - If not, skip this job and move to the next one in the same page.
   - Stop after extracting data from 1 unique jobs.

4. Continue Extraction for Remaining Jobs
   - Move directly to the next job and repeat only the extraction process (Step 3).
   - Do not re-enter search criteria or reload job listings.
"""

initial_actions = [
    {'open_tab': {'url': 'https://www.linkedin.com/jobs/'}}
]

# Create an agent for the task description
agent = Agent(
    task=task_description,
    llm=llm,
    controller=controller,
    browser=browser,
    initial_actions=initial_actions
)

# If you intended to use a list of agents, ensure it's defined
agents = [agent]  # Add the agent to a list if you plan to iterate over multiple agents

async def main():
    for agent in agents:  # Ensure 'agents' is defined
        history = await agent.run()
        result = history.final_result()
        print("Final Result:", result)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Convert the result to JSON format using the LLM
        prompt = f"""
        Here's the extracted job data:
        ---
        {result}
        ---
        Convert the above data into valid JSON format. Ensure that all fields are correctly formatted and any necessary corrections are made.
        """

        # try:
        #     json_response = model.generate_content(prompt)
        #     print(json_response)
        #     json_data = json.loads(json_response)
        #     print("JSON Data:", json_data)
        # except AttributeError as e:
        #     print(f"Error: {e}")
        # except json.JSONDecodeError as e:
        #     print(f"Error decoding JSON: {e}")
        #     print("Response was:", json_response)
        print("==================json data ======================", )

        print("JSON Data: ======", model.generate_content(prompt))

    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())