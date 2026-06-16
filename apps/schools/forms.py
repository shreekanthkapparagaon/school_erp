from django import forms

from apps.accounts.models import User

from .models import School, SchoolClass, Subject, TeacherSubjectAssignment


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ("name", "code", "phone", "address")


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ("school", "name", "code")

    def __init__(self, *args, manager=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager
        if manager and manager.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
            self.fields["school"].initial = manager.school
            self.fields["school"].disabled = True

    def save(self, commit=True):
        subject = super().save(commit=False)
        if self.manager and self.manager.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
            subject.school = self.manager.school
        if commit:
            subject.save()
        return subject


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ("school", "name", "section", "subjects")
        widgets = {"subjects": forms.CheckboxSelectMultiple}

    def __init__(self, *args, manager=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager
        school = getattr(manager, "school", None)
        if school and manager.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
            self.fields["school"].initial = school
            self.fields["school"].disabled = True
            self.fields["subjects"].queryset = Subject.objects.filter(school=school)

    def save(self, commit=True):
        school_class = super().save(commit=False)
        if self.manager and self.manager.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
            school_class.school = self.manager.school
        if commit:
            school_class.save()
            self.save_m2m()
        return school_class


class TeacherSubjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherSubjectAssignment
        fields = ("school", "teacher", "subject", "school_class")

    def __init__(self, *args, manager=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager
        school = getattr(manager, "school", None)
        if school and manager.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
            self.fields["school"].initial = school
            self.fields["school"].disabled = True
            self.fields["teacher"].queryset = self.fields["teacher"].queryset.filter(
                school=school, role="teacher"
            )
            self.fields["subject"].queryset = Subject.objects.filter(school=school)
            self.fields["school_class"].queryset = SchoolClass.objects.filter(school=school)
        else:
            self.fields["teacher"].queryset = self.fields["teacher"].queryset.filter(role="teacher")

    def save(self, commit=True):
        assignment = super().save(commit=False)
        if self.manager:
            assignment.assigned_by = self.manager
            if self.manager.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
                assignment.school = self.manager.school
        if commit:
            assignment.save()
        return assignment
