import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Set up Groq API key
load_dotenv(override=True)  # Load environment variables from .env file and override
groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key  # Set the Groq API key from environment variables

# Initialize the ChatGroq model with a supported model
llm = ChatGroq(model_name="llama-3.3-70b-versatile")

def analyze_resume(full_resume, job_description):
    # Template for analyzing the resume against the job description
    template = """
    You are an AI assistant specialized in resume analysis and recruitment. Analyze the given resume and compare it with the job description. 
    
    Example Response Structure:
    
    **OVERVIEW**:
    - **Match Percentage**: [Calculate overall match percentage between the resume and job description]
    - **Matched Skills**: [List the skills in job description that match the resume]
    - **Unmatched Skills**: [List the skills in the job description that are missing in the resume]

    **DETAILED ANALYSIS**:
    Provide a detailed analysis about:
    1. Overall match percentage between the resume and job description
    2. List of skills from the job description that match the resume
    3. List of skills from the job description that are missing in the resume
    
    **Additional Comments**:
    Additional comments about the resume and suggestions for the recruiter or HR manager.

    Resume: {resume}
    Job Description: {job_description}

    Analysis:
    """
    prompt = PromptTemplate(  # Create a prompt template with input variables
        input_variables=["resume", "job_description"],
        template=template
    )

    # Create a chain combining the prompt and the language model
    chain = prompt | llm

    # Invoke the chain with input data
    response = chain.invoke({"resume": full_resume, "job_description": job_description})

    # Return the content of the response
    return response.content


def optimize_resume(full_resume, job_description):
    """Ask the LLM to produce an optimized resume and structured suggestions as JSON.

    Expected JSON keys:
      - optimized_resume: string (full rewritten resume)
      - suggested_adds: [str]
      - suggested_removals: [str]
      - matched_skills: [str]
      - unmatched_skills: [str]
    """
    template = """
    You are an expert resume writer and recruiter. Given the resume and the job description, produce a JSON object ONLY (no additional commentary) with the following keys:
    - optimized_resume: a polished, ATS-friendly rewrite of the resume tailored to the job description.
    - suggested_adds: an array of short phrases (skills or keywords) the candidate should add.
    - suggested_removals: an array of short phrases (lines or items) that could be removed or de-emphasized.
    - matched_skills: an array of skills from the job description that appear in the resume.
    - unmatched_skills: an array of skills from the job description missing in the resume.

    Resume: {resume}
    Job Description: {job_description}

    IMPORTANT: Output must be valid JSON. Use arrays and strings. Do not include any markdown or surrounding text.
    """

    prompt = PromptTemplate(
        input_variables=["resume", "job_description"],
        template=template,
    )

    chain = prompt | llm
    response = chain.invoke({"resume": full_resume, "job_description": job_description})
    text = response.content

    # Try to extract JSON from the response
    try:
        # Find the first JSON object in the text
        start = text.find('{')
        if start != -1:
            json_text = text[start:]
        else:
            json_text = text
        data = json.loads(json_text)
        return data
    except Exception:
        # If parsing failed, fall back to returning raw text in a predictable structure
        return {
            "optimized_resume": text,
            "suggested_adds": [],
            "suggested_removals": [],
            "matched_skills": [],
            "unmatched_skills": [],
        }
