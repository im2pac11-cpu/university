from ..models import Enrollment


class BaseEnrollmentPolicy:
    def get_queryset(self, user):
        return Enrollment.objects.none()


class AdminEnrollmentPolicy(BaseEnrollmentPolicy):
    def get_queryset(self, user):
        return Enrollment.objects.all()


class ProfessorEnrollmentPolicy(BaseEnrollmentPolicy):
    def get_queryset(self, user):
        return Enrollment.objects.filter(
            course_group__professor=user
        )


class StudentEnrollmentPolicy(BaseEnrollmentPolicy):
    def get_queryset(self, user):
        student = getattr(user, "student_profile", None)
        if not student:
            return Enrollment.objects.none()

        return Enrollment.objects.filter(
            student=student,
            semester__is_active=True
        )


ENROLLMENT_POLICIES = {
    "admin": AdminEnrollmentPolicy(),
    "professor": ProfessorEnrollmentPolicy(),
    "student": StudentEnrollmentPolicy(),
}
