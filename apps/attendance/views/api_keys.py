import secrets

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from apps.plans.utils import manager_required
from apps.schools.models import School

from ..models import AttendanceAPIKey


@login_required
@manager_required
def api_key_list(request):
    api_keys = (
        AttendanceAPIKey.objects
        .select_related("school")
        .order_by("school__name")
    )

    paginator = Paginator(api_keys, 10)

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "attendance/api_key_list.html",
        {
            "api_keys": page_obj,
            "page_obj": page_obj,
            "paginator": paginator,
        },
    )


@login_required
@manager_required
@transaction.atomic
def api_key_create(request):
    if request.method == "POST":
        school_id = request.POST.get("school")

        school = get_object_or_404(
            School,
            pk=school_id,
        )

        if AttendanceAPIKey.objects.filter(
            school=school
        ).exists():
            messages.error(
                request,
                "This school already has an attendance API key.",
            )
            return redirect(
                "attendance:api_key_list"
            )

        api_key = AttendanceAPIKey.objects.create(
            school=school,
        )

        request.session["new_attendance_api_key"] = (
            api_key.key
        )

        messages.success(
            request,
            f"Attendance API key created for {school.name}.",
        )

        return redirect(
            "attendance:api_key_detail",
            pk=api_key.pk,
        )

    schools = (
        School.objects
        .exclude(attendance_api_key__isnull=False)
        .order_by("name")
    )

    return render(
        request,
        "attendance/api_key_create.html",
        {
            "schools": schools,
        },
    )


@login_required
@manager_required
def api_key_detail(request, pk):
    api_key = get_object_or_404(
        AttendanceAPIKey.objects.select_related("school"),
        pk=pk,
    )

    new_key = request.session.pop(
        "new_attendance_api_key",
        None,
    )

    return render(
        request,
        "attendance/api_key_detail.html",
        {
            "api_key": api_key,
            "new_key": new_key,
        },
    )


@login_required
@manager_required
@transaction.atomic
def api_key_toggle(request, pk):
    if request.method != "POST":
        return redirect(
            "attendance:api_key_list"
        )

    api_key = get_object_or_404(
        AttendanceAPIKey,
        pk=pk,
    )

    api_key.is_active = not api_key.is_active

    api_key.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    if api_key.is_active:
        messages.success(
            request,
            f"API key for {api_key.school.name} activated.",
        )
    else:
        messages.warning(
            request,
            f"API key for {api_key.school.name} disabled.",
        )

    return redirect(
        "attendance:api_key_list"
    )


@login_required
@manager_required
@transaction.atomic
def api_key_regenerate(request, pk):
    if request.method != "POST":
        return redirect(
            "attendance:api_key_list"
        )

    api_key = get_object_or_404(
        AttendanceAPIKey,
        pk=pk,
    )

    api_key.key = secrets.token_urlsafe(48)

    api_key.save(
        update_fields=[
            "key",
            "updated_at",
        ]
    )

    request.session["new_attendance_api_key"] = (
        api_key.key
    )

    messages.success(
        request,
        f"API key for {api_key.school.name} regenerated.",
    )

    return redirect(
        "attendance:api_key_detail",
        pk=api_key.pk,
    )