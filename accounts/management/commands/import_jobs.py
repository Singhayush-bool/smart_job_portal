import csv
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model
from accounts.models import Job, Company, Industry, JobCategory, Skill

User = get_user_model()


class Command(BaseCommand):
    help = "Import jobs from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs["csv_file"]

        # Database se ek default employer/user dhoondhein taaki Company ke sath link ho sake
        default_employer = (
            User.objects.filter(role="EMPLOYER").first() or User.objects.first()
        )

        if not default_employer:
            self.stdout.write(
                self.style.ERROR(
                    "Error: Koi bhi user database mein nahi mila jise Company ka employer banaya ja sake. Pehle ek user register karein!"
                )
            )
            return

        try:
            with open(csv_file_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                count = 0

                for row in reader:
                    # 1. Company Handle karein (employer default set karke)
                    company_name = row["company"].strip()
                    company_obj, created = Company.objects.get_or_create(
                        name=company_name, defaults={"employer": default_employer}
                    )

                    # 2. Category Handle karein
                    category_obj = None
                    if row.get("category"):
                        category_obj, _ = JobCategory.objects.get_or_create(
                            name=row["category"].strip()
                        )

                    # 3. Industry Handle karein
                    industry_obj = None
                    if row.get("industry"):
                        industry_obj, _ = Industry.objects.get_or_create(
                            name=row["industry"].strip()
                        )

                    # 4. Job Create karein
                    job = Job.objects.create(
                        title=row["title"].strip(),
                        company=company_obj,
                        description=row["description"].strip(),
                        category=category_obj,
                        industry=industry_obj,
                        location=row["location"].strip(),
                        salary_min=row["salary_min"] or None,
                        salary_max=row["salary_max"] or None,
                        experience_min=row["experience_min"] or 0,
                        experience_max=row["experience_max"] or None,
                        employment_type=row["employment_type"].strip(),
                        work_mode=row["work_mode"].strip(),
                        expires_at=(
                            parse_datetime(row["expires_at"])
                            if row.get("expires_at")
                            else None
                        ),
                        is_active=True,
                    )

                    # 5. Skills Handle karein
                    if row.get("skills"):
                        skills_list = [s.strip() for s in row["skills"].split(",")]
                        skill_objs = []
                        for skill_name in skills_list:
                            skill_obj, _ = Skill.objects.get_or_create(name=skill_name)
                            skill_objs.append(skill_obj)

                        job.skills.set(skill_objs)

                    count += 1

                self.stdout.write(
                    self.style.SUCCESS(f"Successfully imported {count} jobs!")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing jobs: {e}"))
