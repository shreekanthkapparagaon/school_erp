import uuid
from django.utils import timezone

def generate_receipt_number():
    from apps.fees.models.student_fee import StudentFee
    date_part = timezone.localdate().strftime("%Y%m%d")
    return f"RCPT-{date_part}-{uuid.uuid4().hex[:8].upper()}"
