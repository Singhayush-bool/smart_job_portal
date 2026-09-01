import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render


def generate_job_description(request):
    if request.method == "POST":
        job_title = request.POST.get("job_title", "").strip()
        skills = request.POST.get("skills", "").strip()
        experience_level = request.POST.get("experience_level", "").strip()

        api_key = getattr(settings, "GEMINI_API_KEY", "")

        prompt = f"""
        Write a detailed and professional Job Description for:
        - Job Title: {job_title}
        - Required Skills: {skills}
        - Experience Level: {experience_level}

        Format with clear sections: Role Overview, Key Responsibilities, and Required Qualifications.
        """

        # Working production models list
        models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

        for model_name in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            try:
                res = requests.post(url, json=payload, timeout=12)
                data = res.json()

                if res.status_code == 200 and "candidates" in data:
                    text_output = data["candidates"][0]["content"]["parts"][0]["text"]
                    return JsonResponse({"job_description": text_output})
            except Exception:
                continue

        # Guaranteed Fallback JD (Generates instantly if API fails or key is invalid)
        fallback_jd = f"""📌 Job Title: {job_title}
📍 Experience Level: {experience_level}
🛠 Key Skills: {skills}

---

### Role Overview
We are looking for a skilled {job_title} to join our growing team. In this role, you will be responsible for developing high-quality solutions using {skills}.

### Key Responsibilities
• Design, build, and maintain efficient, reusable, and reliable code.
• Collaborate with cross-functional teams to define, design, and ship new features.
• Identify and fix performance bottlenecks and bugs.
• Participate in code reviews and support continuous application improvement.

### Requirements & Qualifications
• Professional experience as a {job_title} ({experience_level}).
• Strong expertise in {skills}.
• Good understanding of software engineering best practices.
• Excellent analytical and problem-solving skills.
"""
        return JsonResponse({"job_description": fallback_jd})

    return render(request, "ai_employer/generate_jd.html")
