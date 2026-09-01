import json


def generate_job_posting_schema(job, request):
    """Generates Schema.org JobPosting JSON-LD for Google Jobs"""
    schema_data = {
        "@context": "https://schema.org/",
        "@type": "JobPosting",
        "title": job.title,
        "description": job.description,
        "identifier": {
            "@type": "PropertyValue",
            "name": job.company.name,
            "value": str(job.id),
        },
        "datePosted": job.created_at.strftime("%Y-%m-%d"),
        "validThrough": (
            job.expires_at.strftime("%Y-%m-%d") if job.expires_at else None
        ),
        "employmentType": job.employment_type.upper().replace(" ", "_"),
        "hiringOrganization": {
            "@type": "Organization",
            "name": job.company.name,
            "sameAs": job.company.website if job.company.website else "",
            "logo": (
                request.build_absolute_uri(job.company.logo.url)
                if job.company.logo
                else ""
            ),
        },
        "jobLocation": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": job.location,
                "addressCountry": "IN",
            },
        },
    }

    if job.salary_min and job.salary_max:
        schema_data["baseSalary"] = {
            "@type": "MonetaryAmount",
            "currency": "INR",
            "value": {
                "@type": "QuantitativeValue",
                "minValue": float(job.salary_min),
                "maxValue": float(job.salary_max),
                "unitText": "YEAR",
            },
        }

    return json.dumps(schema_data)
