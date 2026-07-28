"""
Reusable object factories for the Results test suite.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model

from apps.plans.models import Feature, Plan, PlanFeature, Subscription
from apps.results.models import Exam, Result
from apps.schools.models import School, SchoolClass, Subject

User = get_user_model()


def create_school(
    name="Test School",
    code="TS001",
):
    return School.objects.create(
        name=name,
        code=code,
        phone="9999999999",
        address="Test Address",
    )


def create_feature(
    code="results",
    name="Results",
):
    return Feature.objects.create(
        code=code,
        name=name,
        default_enabled=True,
    )


def create_plan(
    feature=None,
    slug="test-plan",
    name="Test Plan",
):
    plan = Plan.objects.create(
        slug=slug,
        name=name,
    )

    if feature:
        PlanFeature.objects.create(
            plan=plan,
            feature=feature,
        )

    return plan


def create_subscription(
    school,
    plan,
):
    return Subscription.objects.create(
        school=school,
        plan=plan,
    )


def create_user(
    *,
    email,
    role,
    school,
    school_class=None,
    password="TestPassword@123",
    **extra,
):
    return User.objects.create_user(
        email=email,
        password=password,
        role=role,
        school=school,
        school_class=school_class,
        first_name=email.split("@")[0].title(),
        last_name="User",
        **extra,
    )


def create_class(
    school,
    name="10",
    section="A",
):
    return SchoolClass.objects.create(
        school=school,
        name=name,
        section=section,
    )


def create_subject(
    *,
    school,
    created_by,
    name="Mathematics",
    code="MATH101",
):
    return Subject.objects.create(
        school=school,
        name=name,
        code=code,
        created_by=created_by,
    )


def assign_subject(
    school_class,
    subject,
):
    school_class.subjects.add(subject)
    return school_class


def create_exam(
    *,
    school,
    created_by,
    school_class=None,
    name="Unit Test",
    academic_year="2026-2027",
    status=Exam.Status.DRAFT,
):
    exam = Exam.objects.create(
        school=school,
        name=name,
        academic_year=academic_year,
        status=status,
        created_by=created_by,
    )

    if school_class:
        exam.classes.add(school_class)

    return exam


def create_result(
    *,
    school,
    school_class,
    student,
    subject,
    exam,
    created_by,
    marks=80,
    max_marks=100,
):
    return Result.objects.create(
        school=school,
        school_class=school_class,
        student=student,
        subject=subject,
        exam=exam,
        marks_obtained=Decimal(str(marks)),
        max_marks=Decimal(str(max_marks)),
        created_by=created_by,
    )


def create_complete_school():
    """
    Returns a dictionary containing a fully configured
    school ready for testing.
    """

    school = create_school()

    feature = create_feature()

    plan = create_plan(feature=feature)

    create_subscription(
        school=school,
        plan=plan,
    )

    manager = create_user(
        email="manager@test.com",
        role=User.Role.MANAGER,
        school=school,
    )

    principal = create_user(
        email="principal@test.com",
        role=User.Role.PRINCIPAL,
        school=school,
    )

    head = create_user(
        email="head@test.com",
        role=User.Role.HEAD,
        school=school,
    )

    teacher = create_user(
        email="teacher@test.com",
        role=User.Role.TEACHER,
        school=school,
    )

    school_class = create_class(school)

    student = create_user(
        email="student@test.com",
        role=User.Role.STUDENT,
        school=school,
        school_class=school_class,
    )

    subject = create_subject(
        school=school,
        created_by=manager,
    )

    assign_subject(
        school_class,
        subject,
    )

    exam = create_exam(
        school=school,
        created_by=manager,
        school_class=school_class,
        status=Exam.Status.ACTIVE,
    )

    result = create_result(
        school=school,
        school_class=school_class,
        student=student,
        subject=subject,
        exam=exam,
        created_by=teacher,
    )

    return {
        "school": school,
        "feature": feature,
        "plan": plan,
        "manager": manager,
        "principal": principal,
        "head": head,
        "teacher": teacher,
        "student": student,
        "school_class": school_class,
        "subject": subject,
        "exam": exam,
        "result": result,
    }