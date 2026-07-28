from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render

from apps.accounts.models import User
from apps.plans.utils import feature_action_required,has_feature_action_permission
from apps.results.models import Exam
from ..utils.exam_utils import populate_exam_progress
from ..utils.dashboard_utils import RESULT_DASHBOARD_CARDS


@login_required
@feature_action_required(
    "results",
    "view",
    "Your current subscription does not include Results.",
)
def result_home(request):

    visible_cards = []

    for card in RESULT_DASHBOARD_CARDS:

        if request.user.role not in card["roles"]:
            continue

        if card.get("coming_soon"):
            visible_cards.append(card)
            continue

        if has_feature_action_permission(
            request.user,
            card["feature"],
            card["action"],
        ):

            card = card.copy()
            card["url"] = card["url"]()
            visible_cards.append(card)

    return render(
        request,
        "results/home.html",
        {
            "cards": visible_cards,
        },
    )

@login_required
@feature_action_required(
    "results",
    "view",
    "Your current subscription does not include Results.",
)
def result_entry_home(request):
    if request.user.role == User.Role.STUDENT:
        if request.user.school_class_id:
            return redirect(
                "results:class_results",
                class_id=request.user.school_class_id,
            )

        messages.info(request, "No class has been assigned.")
        return redirect("accounts:role_redirect")

    if request.user.role not in (
        User.Role.HEAD,
        User.Role.PRINCIPAL,
        User.Role.TEACHER,
    ):
        messages.error(request, "You do not have permission.")
        return redirect("accounts:role_redirect")

    exams = (
        Exam.objects.filter(
            school=request.user.school,
            status__in=[
                Exam.Status.ACTIVE,
                Exam.Status.COMPLETED,
                Exam.Status.PUBLISHED,
            ],
        )
        .annotate(
            class_count=Count("classes", distinct=True),
            student_count=Count("classes__students", distinct=True),
            subject_count=Count("classes__subjects", distinct=True),
            result_count=Count("results", distinct=True),
        )
        .order_by("-created_at")
    )

    populate_exam_progress(exams)

    context = {
        "exams": exams,
    }

    return render(
        request,
        "results/result_entry.html",
        context,
    )

