from ..models import CourseGroup

class BaseCourseGroupPolicy:
    def get_queryset(self, user):
        return CourseGroup.objects.none()


class AdminCourseGroupPolicy(BaseCourseGroupPolicy):
    def get_queryset(self, user):
        return CourseGroup.objects.all()


class ProfessorCourseGroupPolicy(BaseCourseGroupPolicy):
    def get_queryset(self, user):
        return CourseGroup.objects.filter(
            professor=user
        )


class StudentCourseGroupPolicy(BaseCourseGroupPolicy):
    def get_queryset(self, user):
        return CourseGroup.objects.filter(
            semester__is_active=True
        )


COURSE_GROUP_POLICIES = {
    "admin": AdminCourseGroupPolicy(),
    "professor": ProfessorCourseGroupPolicy(),
    "student": StudentCourseGroupPolicy(),
}
