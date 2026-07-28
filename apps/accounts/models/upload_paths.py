import os


def profile_upload_to(instance, filename):
    user = instance.profile.user
    email_slug = user.email.replace("@", "_at_").replace(".", "_")
    role_folder = user.role or "unknown"
    return (
        f"profiles/"
        f"{role_folder}/"
        f"{email_slug}/"
        f"{instance.field.slug}/"
        f"{filename}"
    )


def profile_image_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"profiles/user_{instance.user.id}/profile{ext}"