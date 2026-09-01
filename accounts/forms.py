from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import (
    User,
    JobSeekerProfile,
    JobSeekerSkill,
    Education,
    Experience,
    Resume,
    Company,
    Job,
    Post,
    Certification,
)

User = get_user_model()

# =========================================================
# REGISTER FORM
# =========================================================


from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
        ]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Username"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "First Name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Last Name"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Phone Number"}
            ),
            "role": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agar 'role' field choices wala hai, toh usme se 'admin' ko hata dein
        if "role" in self.fields:
            # Maan lijiye aapke choices ('job_seeker', 'Job Seeker'), ('employer', 'Employer'), ('admin', 'Admin') hain
            allowed_roles = [
                choice
                for choice in self.fields["role"].choices
                if choice[0].lower() not in ["admin", "administrator"]
            ]
            self.fields["role"].choices = allowed_roles


# =========================================================
# JOB SEEKER PROFILE FORM
# =========================================================


class JobSeekerProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
    )

    class Meta:
        model = JobSeekerProfile
        fields = [
            "phone",
            "date_of_birth",
            "gender",
            "location",
            "bio",
            "linkedin_url",
            "github_url",
            "portfolio_url",
            "profile_image",
        ]
        widgets = {
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Phone Number",
                }
            ),
            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "gender": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Gender",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Location",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Tell something about yourself...",
                    "rows": 5,
                }
            ),
            "linkedin_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "LinkedIn URL",
                }
            ),
            "github_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "GitHub URL",
                }
            ),
            "portfolio_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Portfolio URL",
                }
            ),
            "profile_image": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Profile Image URL",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name


# =========================================================
# EDUCATION
# =========================================================


class EducationForm(forms.ModelForm):

    class Meta:
        model = Education
        fields = [
            "institution",
            "degree",
            "field_of_study",
            "start_year",
            "end_year",
            "description",
        ]
        widgets = {
            "institution": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Institution"}
            ),
            "degree": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Degree"}
            ),
            "field_of_study": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Field of Study"}
            ),
            "start_year": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Start Year"}
            ),
            "end_year": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "End Year"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Education description",
                    "rows": 4,
                }
            ),
        }


# =========================================================
# EXPERIENCE
# =========================================================


class ExperienceForm(forms.ModelForm):

    class Meta:
        model = Experience
        fields = [
            "company_name",
            "job_title",
            "location",
            "start_date",
            "end_date",
            "is_current",
            "description",
        ]
        widgets = {
            "company_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Company Name"}
            ),
            "job_title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Job Title"}
            ),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Job Location"}
            ),
            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "is_current": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Describe your work experience...",
                    "rows": 5,
                }
            ),
        }


# =========================================================
# JOB SEEKER SKILL
# =========================================================


class JobSeekerSkillForm(forms.ModelForm):

    class Meta:
        model = JobSeekerSkill
        fields = [
            "skill",
            "experience_years",
        ]
        widgets = {
            "skill": forms.Select(attrs={"class": "form-select"}),
            "experience_years": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Experience in years",
                    "step": "0.1",
                    "min": "0",
                }
            ),
        }


# =========================================================
# RESUME
# =========================================================


class ResumeForm(forms.ModelForm):

    class Meta:
        model = Resume
        fields = [
            "title",
            "file",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Resume Title"}
            ),
            "file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.doc,.docx",
                }
            ),
        }


# =========================================================
# COMPANY
# =========================================================


class CompanyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = [
            "name",
            "logo",
            "description",
            "website",
            "location",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Company Name"}
            ),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Company Description",
                    "rows": 5,
                }
            ),
            "website": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://example.com"}
            ),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Company Location"}
            ),
        }


# =========================================================
# JOB
# =========================================================

from django import forms
from .models import Job, Company


from django import forms
from .models import Job, Company


class JobForm(forms.ModelForm):
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Type skills separated by comma (e.g. Python, Django, React)",
            }
        ),
        help_text="Enter skills separated by commas.",
    )

    class Meta:
        model = Job
        fields = [
            # "company",  # 🟢 Isko yahan se hata diya hai taaki form mein na dikhe
            "title",
            "description",
            "category",
            "industry",
            "location",
            "salary_min",
            "salary_max",
            "experience_min",
            "experience_max",
            "employment_type",
            "work_mode",
            "skills",
            "expires_at",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Job Title"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Job Description",
                    "rows": 6,
                }
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "industry": forms.Select(attrs={"class": "form-select"}),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Job Location"}
            ),
            "salary_min": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Minimum Salary"}
            ),
            "salary_max": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Maximum Salary"}
            ),
            "experience_min": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Minimum Experience",
                    "min": "0",
                }
            ),
            "experience_max": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Maximum Experience",
                    "min": "0",
                }
            ),
            "employment_type": forms.Select(attrs={"class": "form-select"}),
            "work_mode": forms.Select(attrs={"class": "form-select"}),
            "expires_at": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
        }

    def __init__(self, *args, **kwargs):
        # 🟢 Kyunki ab company field form mein nahi hai, user argument ki bhi zaroorat nahi hai
        kwargs.pop("user", None)
        super().__init__(*args, **kwargs)


# =========================================================
# SOCIAL POST
# =========================================================


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = [
            "content",
            "image",
        ]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "What do you want to share?",
                    "rows": 4,
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }


# =========================================================
# CERTIFICATION FORM
# =========================================================


class CertificationForm(forms.ModelForm):

    class Meta:
        model = Certification
        fields = [
            "name",
            "issuing_organization",
            "issue_date",
            "expiration_date",
            "credential_id",
            "credential_url",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Certification Name"}
            ),
            "issuing_organization": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Issuing Organization"}
            ),
            "issue_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "expiration_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "credential_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Credential ID (Optional)",
                }
            ),
            "credential_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Credential URL (Optional)",
                }
            ),
        }
