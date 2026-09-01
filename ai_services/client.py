import json
from django.conf import settings
from google import genai
from google.genai import types

# New SDK Client Initialization
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Active Model Name Ko Update Karein
MODEL_NAME = "gemini-3.6-flash"


def query_ai_service(prompt, is_json=True):
    try:
        config = None
        if is_json:
            config = types.GenerateContentConfig(response_mime_type="application/json")

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config,
        )

        if is_json:
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)

        return response.text

    except Exception as e:
        if is_json:
            return {"error": str(e)}
        return f"Error processing AI request: {str(e)}"


def scan_resume_against_jd(resume_text, job_description):
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) Scanner.
    Compare the following Resume with the Job Description.

    JOB DESCRIPTION:
    {job_description}

    RESUME TEXT:
    {resume_text}

    Analyze carefully and provide JSON output only with this schema:
    {{
        "match_percentage": 75,
        "can_apply": true,
        "verdict": "Aap is resume ke sath apply kar sakte hain!",
        "matching_skills": ["Python", "Django", "REST API"],
        "missing_skills": ["Docker", "Redis"],
        "improvement_suggestions": "Resume mein Docker containerization projects add karein."
    }}
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        return {"error": f"ATS Scan failed: {str(e)}"}
