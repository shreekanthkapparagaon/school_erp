from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect

from apps.plans.utils import feature_action_required
from ..models import Exam


@login_required
@feature_action_required(
    "results",
    "approve",
    "You do not have permission to manage examinations.",
)
def activate_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)

    try:
        exam.activate()
        messages.success(
            request,
            "Examination activated successfully.",
        )
    except ValidationError as e:
        messages.error(request, e.message)

    return redirect(
        "results:exam_detail",
        exam_id=exam.pk,
    )

@login_required
@feature_action_required(
    "results",
    "approve",
    "You do not have permission to manage examinations.",
)
def complete_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)

    try:
        exam.complete()
        messages.success(
            request,
            "Examination marked as completed.",
        )
    except ValidationError as e:
        messages.error(request, e.message)

    return redirect(
        "results:exam_detail",
        exam_id=exam.pk,
    )

@login_required
@feature_action_required(
    "results",
    "publish",
    "You do not have permission to manage examinations.",
)
def publish_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)

    try:
        exam.publish()
        messages.success(
            request,
            "Results published successfully.",
        )
    except ValidationError as e:
        messages.error(request, e.message)

    return redirect(
        "results:exam_detail",
        exam_id=exam.pk,
    )