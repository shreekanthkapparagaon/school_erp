from .class_views import (
    class_detail,
    class_list,
    create_class,
    delete_class,
    promote_class,
    update_class,
)
from .school_views import (
    create_school,
    delete_school,
    school_detail,
    school_list,
    update_school,
)
from .subject_views import (
    create_subject,
    delete_subject,
    subject_detail,
    subject_list,
    update_subject,
)
from .teacher_assignment_views import (
    assignment_detail,
    assignment_list,
    create_assignment,
    delete_assignment,
    update_assignment,
)

__all__ = [
    "school_list",
    "create_school",
    "school_detail",
    "update_school",
    "delete_school",
    "subject_list",
    "create_subject",
    "subject_detail",
    "update_subject",
    "delete_subject",
    "class_list",
    "create_class",
    "class_detail",
    "update_class",
    "promote_class",
    "delete_class",
    "assignment_list",
    "create_assignment",
    "assignment_detail",
    "update_assignment",
    "delete_assignment",
]