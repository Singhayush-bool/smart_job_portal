import docx
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from pypdf import PdfReader

from ai_services.client import query_ai_service
from .models import AICoverLetter, AIResumeAnalysis


def extract_text_from_file(uploaded_file):
    text = ""
    try:
        if uploaded_file.name.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
        elif uploaded_file.name.endswith(".docx"):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        print(f"File extraction error: {e}")
    return text.strip()


@login_required
def analyze_resume(request):
    context = {}

    if request.method == "POST":
        job_title = request.POST.get("job_title", "").strip()
        job_description = request.POST.get("job_description", "").strip()
        resume_text = request.POST.get("resume_text", "").strip()
        action_type = request.POST.get("action_type")

        # 1. File se Text Extract karein agar File Upload hui hai
        if "resume_file" in request.FILES:
            file_text = extract_text_from_file(request.FILES["resume_file"])
            if file_text:
                resume_text = file_text

        # Re-populate inputs so data doesn't disappear on form submit
        context["extracted_text"] = resume_text
        context["job_title"] = job_title
        context["job_description"] = job_description

        # Validation Check
        if not resume_text and action_type in [
            "analyze_resume",
            "generate_cover_letter",
        ]:
            context["error"] = (
                "Kripya Resume File upload karein ya Resume Text paste karein."
            )
            return render(request, "ai_jobseeker/analyze_resume.html", context)

        # ACTION 1: RESUME MATCH & ATS SCAN
        if action_type == "analyze_resume":
            prompt = f"""
            Act as an expert ATS Scanner. Compare the resume with the job description for '{job_title}'.
            Return ONLY valid JSON:
            {{
                "ats_score": 85,
                "resume_score": 80,
                "skill_gaps": ["Docker", "AWS"],
                "suggested_improvements": ["Add quantitative metrics", "Highlight key projects"]
            }}

            Resume: {resume_text}
            Job Description: {job_description}
            """
            result = query_ai_service(prompt, is_json=True)

            if isinstance(result, dict) and "error" not in result:
                AIResumeAnalysis.objects.create(
                    user=request.user,
                    ats_score=result.get("ats_score", 0),
                    resume_score=result.get("resume_score", 0),
                    skill_gaps=result.get("skill_gaps", []),
                    suggested_improvements=result.get("suggested_improvements", []),
                )
                context["result_type"] = "analysis"
                context["ats_score"] = result.get("ats_score", 0)
                context["resume_score"] = result.get("resume_score", 0)
                context["missing_skills"] = result.get("skill_gaps", [])
                context["suggestions"] = result.get("suggested_improvements", [])
            else:
                context["error"] = (
                    f"AI Error: {result.get('error') if isinstance(result, dict) else result}"
                )

        # ACTION 2: COVER LETTER GENERATION
        elif action_type == "generate_cover_letter":
            prompt = f"""
            Write a professional cover letter for the role '{job_title}'.
            Resume details: {resume_text}
            Job description: {job_description}
            """
            letter_text = query_ai_service(prompt, is_json=False)

            if letter_text and "Error" not in str(letter_text):
                AICoverLetter.objects.create(
                    user=request.user,
                    job_title=job_title,
                    company_name="Target Company",
                    generated_content=str(letter_text),
                )
                context["result_type"] = "cover_letter"
                context["cover_letter_content"] = letter_text
            else:
                context["error"] = f"AI Generation Failed: {letter_text}"

        # ACTION 3: AI JD GENERATION
        elif action_type == "generate_jd":
            prompt = f"Generate a detailed Job Description for the role '{job_title}'."
            jd_text = query_ai_service(prompt, is_json=False)
            context["job_description"] = jd_text
            context["result_type"] = "generated_jd"
            context["generated_jd_content"] = jd_text

    return render(request, "ai_jobseeker/analyze_resume.html", context)


generate_cover_letter = analyze_resume
