import cloudinary
import cloudinary.uploader
from django.conf import settings

cloudinary.config(
    cloud_name=getattr(settings, "CLOUDINARY_CLOUD_NAME", ""),
    api_key=getattr(settings, "CLOUDINARY_API_KEY", ""),
    api_secret=getattr(settings, "CLOUDINARY_API_SECRET", ""),
)


def upload_resume_to_cloud(file_obj, folder="resumes"):
    try:
        result = cloudinary.uploader.upload(
            file_obj, folder=folder, resource_type="auto"
        )
        return {"status": "success", "url": result.get("secure_url")}
    except Exception as e:
        return {"status": "error", "message": str(e)}
