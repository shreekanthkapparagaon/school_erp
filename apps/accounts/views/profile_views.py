from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from datetime import datetime

from apps.accounts.utils.profile import get_profile_cards

from ..forms import ProfileUpdateForm
from ..models import ProfileField


@login_required
def profile_detail(request):

    user = request.user
    profile = user.profile

    # --------------------------------------------------
    # Determine edit section
    # --------------------------------------------------

    if request.method == "POST":
        edit_section = request.POST.get("section", "").lower()
    else:
        edit_section = request.GET.get("edit", "").lower()

    basic_edit = edit_section == "basic"
    additional_edit = edit_section == "additional"
    photo_edit = edit_section == "photo"

    edit_mode = any(
        (
            basic_edit,
            additional_edit,
            photo_edit,
        )
    )

    # --------------------------------------------------
    # Form
    # --------------------------------------------------

    form = ProfileUpdateForm(
        data=request.POST or None,
        files=request.FILES or None,
        instance=profile,
        section=edit_section,
    )

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    if request.method == "POST":

        # ----------------------------------------------
        # Remove photo
        # ----------------------------------------------

        if "remove_profile_image" in request.POST:

            if profile.profile_image:
                profile.profile_image.delete(save=False)

                profile.profile_image = None

                profile.save(
                    update_fields=["profile_image"]
                )

            messages.success(
                request,
                "Profile photo removed successfully.",
            )

            return redirect("accounts:profile")

        # ----------------------------------------------
        # Photo
        # ----------------------------------------------

        if photo_edit:

            image = request.FILES.get("profile_image")

            if not image:

                messages.error(
                    request,
                    "Please choose a profile photo.",
                )

            elif (
                image.size
                > ProfileUpdateForm.MAX_PROFILE_IMAGE_SIZE
            ):

                messages.error(
                    request,
                    "Profile image must be smaller than 1 MB.",
                )

            else:

                profile.profile_image = image

                profile.save(
                    update_fields=["profile_image"]
                )

                messages.success(
                    request,
                    "Profile photo updated successfully.",
                )

                return redirect(
                    "accounts:profile"
                )

        # ----------------------------------------------
        # Basic / Additional
        # ----------------------------------------------

        elif basic_edit or additional_edit:

            if form.is_valid():

                form.save()

                messages.success(
                    request,
                    "Profile updated successfully.",
                )

                return redirect(
                    "accounts:profile"
                )

            else:

                messages.error(
                    request,
                    "Please correct the errors below.",
                )

    # --------------------------------------------------
    # Basic information
    # --------------------------------------------------

    basic_info = [
        {
            "label": "First Name",
            "value": user.first_name or "-",
            "form_field": form["first_name"],
        },
        {
            "label": "Last Name",
            "value": user.last_name or "-",
            "form_field": form["last_name"],
        },
        {
            "label": "Email",
            "value": user.email,
            "form_field": form["email"],
        },
        {
            "label": "Phone",
            "value": user.phone or "-",
            "form_field": form["phone"],
        },
        {
            "label": "Role",
            "value": user.get_role_display(),
            "form_field": None,
        },
        {
            "label": "School",
            "value": user.school or "-",
            "form_field": None,
        },
        {
            "label": "Class",
            "value": user.school_class or "-",
            "form_field": None,
        },
        {
            "label": "Joined",
            "value": user.date_joined,
            "form_field": None,
        },
    ]

    # --------------------------------------------------
    # Dynamic profile fields
    # --------------------------------------------------

    profile_fields = (
        ProfileField.objects
        .filter(
            role=user.role,
            active=True,
        )
        .order_by(
            "order",
            "name",
        )
    )

    existing_values = {
        value.field_id: value
        for value in profile.values.select_related("field")
    }

    custom_fields = []

    completed_fields = 0

    for profile_field in profile_fields:

        profile_value = existing_values.get(
            profile_field.id
        )

        value = None
        is_new = True

        if profile_value:

            if (
                profile_field.field_type == "file"
                and profile_value.file
            ):

                value = profile_value.file

            elif (
                profile_field.field_type == "date"
                and profile_value.value
            ):

                try:

                    value = datetime.strptime(
                        str(profile_value.value),
                        "%Y-%m-%d",
                    ).date()

                except (
                    ValueError,
                    TypeError,
                ):

                    value = profile_value.value

            else:

                value = profile_value.value

            if value not in (
                None,
                "",
                False,
            ):
                completed_fields += 1

            is_new = False

        custom_fields.append(
            {
                "id": profile_field.id,
                "slug": profile_field.slug,
                "label": profile_field.name,
                "type": profile_field.field_type,
                "required": profile_field.required,
                "help_text": profile_field.help_text,
                "value": value,
                "is_new": is_new,
                "form_field": form[
                    f"profile_{profile_field.id}"
                ],
            }
        )

    # --------------------------------------------------
    # Completion
    # --------------------------------------------------

    total_fields = profile_fields.count()

    completion = (
        round(
            (completed_fields / total_fields) * 100
        )
        if total_fields
        else 100
    )

    if completion == 100:

        completion_badge = {
            "label": "Complete",
            "icon": "✅",
            "class": "success",
        }

    elif completion >= 70:

        completion_badge = {
            "label": "Almost Complete",
            "icon": "🟡",
            "class": "warning",
        }

    else:

        completion_badge = {
            "label": "Incomplete",
            "icon": "🔴",
            "class": "danger",
        }

    # --------------------------------------------------
    # Profile cards
    # --------------------------------------------------

    profile_cards = get_profile_cards(
        request.user
    )

    # --------------------------------------------------
    # Context
    # --------------------------------------------------

    context = {
        "title": "My Profile",

        "profile": profile,

        "form": form,

        "edit_mode": edit_mode,

        "edit_section": edit_section,

        "basic_edit": basic_edit,

        "additional_edit": additional_edit,

        "photo_edit": photo_edit,

        "basic_info": basic_info,

        "custom_fields": custom_fields,

        "completion": completion,

        "completed_fields": completed_fields,

        "completion_badge": completion_badge,

        "total_fields": total_fields,

        "profile_cards": profile_cards,
    }

    return render(
        request,
        "accounts/profile.html",
        context,
    )


