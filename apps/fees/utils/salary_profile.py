from apps.fees.models import TeacherSalary


def get_salary_profile_data(user):
    """
    Return finance data for staff users.
    """

    salary = (
        TeacherSalary.objects
        .filter(teacher=user)
        .order_by("-salary_month")
        .first()
    )

    return {
        "type": "salary",
        "title": "Finance",
        "salary": salary,
        "view_url": "fees:fee_list",
        "view_label": "View Fees",
    }