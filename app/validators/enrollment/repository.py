from django.db.models import Sum
from ...models import Enrollment

class EnrollmentRepository:
    """Handles DB queries related to student enrollments."""

    @staticmethod
    def total_units(student_profile):
        return (
            Enrollment.objects
            .filter(student=student_profile)
            .aggregate(total=Sum("course_group__course__units"))
            .get("total") or 0
        )

    @staticmethod
    def is_enrolled(student_profile, course_group):
        return Enrollment.objects.filter(student=student_profile, course_group=course_group).exists()
