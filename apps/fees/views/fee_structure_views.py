from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from apps.fees.forms import FeeStructureForm
from apps.plans.utils import feature_action_required

from .helpers import (
    can_manage_student_fees,
    get_fee_structure_or_404,
)
from apps.fees.models import FeeStructure


@login_required
@feature_action_required(
    "fees",
    "view",
    "Your current subscription does not include Fee Management.",
)
def fee_structure_list(request):
    if not can_manage_student_fees(request.user):
        messages.error(
            request,
            "Only heads and principals can manage fee structures.",
        )
        return redirect("accounts:role_redirect")

    structures = (
        FeeStructure.objects.filter(
            school_id=request.user.school_id,
        )
        .select_related("school_class")
        .order_by(
            "-academic_year",
            "school_class__name",
        )
    )

    paginator = Paginator(structures, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "fees/fee_structure_list.html",
        {
            "page_obj": page_obj,
            "can_manage": can_manage_student_fees(request.user),
        },
    )


@login_required
@feature_action_required(
    "fees",
    "create",
    "You do not have permission to create fee structures.",
)
def create_fee_structure(request):
    if not can_manage_student_fees(request.user):
        messages.error(
            request,
            "Only heads and principals can create fee structures.",
        )
        return redirect("accounts:role_redirect")

    form = FeeStructureForm(
        request.POST or None,
        principal=request.user,
    )

    if request.method == "POST" and form.is_valid():
        structure = form.save()

        messages.success(
            request,
            "Fee structure created and student fees generated.",
        )

        return redirect(
            "fees:fee_structure_detail",
            structure_id=structure.pk,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Create Fee Structure",
            "submit_label": "Create structure",
        },
    )


@login_required
@feature_action_required(
    "fees",
    "view",
    "You do not have permission to view fee structures.",
)
def fee_structure_detail(request, structure_id):
    structure = get_fee_structure_or_404(structure_id)

    if (
        not can_manage_student_fees(request.user)
        or request.user.school_id != structure.school_id
    ):
        messages.error(
            request,
            "You do not have permission to view that fee structure.",
        )
        return redirect("accounts:role_redirect")

    return render(
        request,
        "fees/fee_structure_detail.html",
        {
            "structure": structure,
            "fees": structure.student_fees.select_related("student"),
        },
    )