from import_export import resources

from .models import Result


class ResultResource(resources.ModelResource):
    class Meta:
        model = Result
        fields = (
            "id",
            "school",
            "school_class",
            "student",
            "subject",
            "exam",
            "exam_name",
            "academic_year",
            "marks_obtained",
            "max_marks",
            "grade",
            "published",
        )
        import_id_fields = ("id",)
        use_transactions = True
