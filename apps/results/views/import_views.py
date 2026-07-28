from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from apps.accounts.models import User
from apps.plans.utils import feature_action_required
from apps.schools.models import (
    SchoolClass,
    Subject,
)

from ..forms import BulkResultImportForm
from ..models import Exam

from ..utils.export_utils import workbook_response
from ..utils.import_utils import import_result_workbook
from ..utils.permissions import can_manage_results
from ..utils.template_utils import generate_result_import_template


@login_required
@feature_action_required(
    "results",
    "import",
    "You do not have permission to import results.",
)
def import_results(request, class_id):
    school_class = get_object_or_404(
        SchoolClass.objects.select_related("school").prefetch_related("subjects"),
        pk=class_id,
    )

    if not can_manage_results(request.user, school_class):
        messages.error(
            request,
            "You do not have permission to import results.",
        )
        return redirect("accounts:role_redirect")

    initial = {}

    if request.method == "GET":
        exam_id = request.GET.get("exam")

        if exam_id:
            initial["exam"] = exam_id

    form = BulkResultImportForm(
        request.POST or None,
        request.FILES or None,
        school_class=school_class,
        initial=initial,
    )

    if request.method == "POST" and form.is_valid():
        try:
            imported = import_result_workbook(
                file=form.cleaned_data["file"],
                exam=form.cleaned_data["exam"],
                school_class=school_class,
                imported_by=request.user,
            )

        except (
            ValueError,
            ValidationError,
            User.DoesNotExist,
            Subject.DoesNotExist,
        ) as exc:
            form.add_error("file", str(exc))

        else:
            messages.success(
                request,
                f"Successfully imported {imported} result(s).",
            )
            return redirect(
                "results:class_results",
                class_id=school_class.pk,
            )

    context = {
        "title": "Import Results",
        "form": form,
        "school_class": school_class,
    }

    return render(
        request,
        "results/import.html",
        context,
    )


@login_required
@feature_action_required(
    "results",
    "import",
    "You do not have permission to import results.",
)
def download_import_template(request, class_id):
    school_class = get_object_or_404(
        SchoolClass.objects.prefetch_related("subjects"),
        pk=class_id,
    )

    if not can_manage_results(request.user, school_class):
        messages.error(
            request,
            "You do not have permission to download the template.",
        )
        return redirect("accounts:role_redirect")

    exam_id = request.GET.get("exam")

    if not exam_id:
        messages.error(
            request,
            "Please select an examination first.",
        )
        return redirect(
            "results:import_results",
            class_id=school_class.pk,
        )

    exam = get_object_or_404(
        Exam,
        pk=exam_id,
        school=school_class.school,
    )

    workbook = generate_result_import_template(
        school_class=school_class,
        exam=exam,
    )

    filename = (
        f"{exam.name}_{school_class}.xlsx"
    )

    return workbook_response(
        workbook,
        filename,
    )
