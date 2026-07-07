from django import forms

from apps.accounts.models import User
from apps.schools.models import SchoolClass

from .models import FeePayment, FeeStructure, StudentFee, TeacherSalary


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = (
            "school_class",
            "title",
            "academic_year",
            "total_amount",
            "due_date",
            "notes",
        )
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, principal=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.principal = principal
        if principal is not None:
            self.instance.school = principal.school
            self.fields["school_class"].queryset = SchoolClass.objects.filter(
                school=principal.school
            ).order_by("name", "section")

    def save(self, commit=True):
        structure = super().save(commit=False)
        if self.principal is not None:
            structure.school = self.principal.school
            if not structure.created_by_id:
                structure.created_by = self.principal
        if commit:
            structure.save()
        return structure


class StudentFeeForm(forms.ModelForm):
    class Meta:
        model = StudentFee
        fields = ("student", "title", "academic_year", "total_amount", "due_date", "notes")
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, manager=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager
        self.instance.school = manager.school
        self.fields["student"].queryset = User.objects.filter(
            role=User.Role.STUDENT,
            school_id=manager.school_id,
        ).order_by("first_name", "last_name", "email")

    def save(self, commit=True):
        fee = super().save(commit=False)
        fee.school = self.manager.school
        if not fee.created_by_id:
            fee.created_by = self.manager
        if commit:
            fee.save()
        return fee


class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ("amount", "payment_date", "method", "reference")
        widgets = {"payment_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, fee=None, manager=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fee = fee
        self.manager = manager
        self.instance.fee = fee
        if not self.is_bound and not self.instance.pk:
            self.fields["amount"].initial = fee.balance

    def save(self, commit=True):
        payment = super().save(commit=False)
        payment.fee = self.fee
        payment.received_by = self.manager
        if commit:
            payment.save()
        return payment


class TeacherSalaryForm(forms.ModelForm):
    salary_month = forms.DateField(
        input_formats=["%Y-%m"],
        widget=forms.DateInput(format="%Y-%m", attrs={"type": "month"}),
    )

    class Meta:
        model = TeacherSalary
        fields = ("teacher", "salary_month", "amount", "status", "paid_on", "notes")
        widgets = {"paid_on": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, principal=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.principal = principal
        self.instance.school = principal.school
        self.fields["teacher"].queryset = User.objects.filter(
            role=User.Role.TEACHER,
            school_id=principal.school_id,
        ).order_by("first_name", "last_name", "email")

    def save(self, commit=True):
        salary = super().save(commit=False)
        salary.school = self.principal.school
        if not salary.created_by_id:
            salary.created_by = self.principal
        if commit:
            salary.save()
        return salary
