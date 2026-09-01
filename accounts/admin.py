from django.contrib import admin

from .models import (
    User,
    JobSeekerProfile,
    Skill,
    JobSeekerSkill,
    Education,
    Experience,
    Resume,
    JobCategory,
    Industry,
    Company,
    Job,
    SavedJob,
    Application,
    Post,
    PostLike,
    PostComment,
    Repost,
    SavedPost,
)


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):

    list_display = (
        "username",
        "email",
        "role",
        "is_verified",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "location",
        "gender",
        "created_at",
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):

    list_display = ("name",)


@admin.register(JobSeekerSkill)
class JobSeekerSkillAdmin(admin.ModelAdmin):

    list_display = (
        "profile",
        "skill",
        "experience_years",
    )


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):

    list_display = (
        "profile",
        "degree",
        "institution",
        "start_year",
        "end_year",
    )


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):

    list_display = (
        "profile",
        "job_title",
        "company_name",
        "start_date",
        "end_date",
        "is_current",
    )


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):

    list_display = (
        "profile",
        "title",
        "file",
        "is_default",
        "uploaded_at",
    )


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "is_active",
    )

    prepopulated_fields = {"slug": ("name",)}


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "is_active",
    )

    prepopulated_fields = {"slug": ("name",)}


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "employer",
        "location",
        "is_verified",
        "created_at",
    )

    list_filter = ("is_verified",)

    search_fields = (
        "name",
        "location",
        "employer__username",
    )


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "company",
        "category",
        "industry",
        "location",
        "employment_type",
        "work_mode",
        "is_approved",
        "is_active",
        "is_featured",
        "is_urgent",
    )

    list_filter = (
        "is_approved",
        "is_active",
        "is_featured",
        "is_urgent",
        "employment_type",
        "work_mode",
    )

    search_fields = (
        "title",
        "company__name",
        "location",
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = (
        "author",
        "content",
        "created_at",
        "is_active",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "author__username",
        "content",
    )


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "post",
        "created_at",
    )


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "post",
        "content",
        "created_at",
        "is_active",
    )

    search_fields = (
        "user__username",
        "content",
    )


@admin.register(Repost)
class RepostAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "post",
        "created_at",
    )


@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "post",
        "created_at",
    )
