from rest_framework.exceptions import ValidationError
from .base_rule import ValidationRule

class DuplicateEnrollmentRule(ValidationRule):
    """Checks that the student is not already enrolled in the course group."""

    def validate(self, student_profile, course_group, semester, repo):
        if repo.is_enrolled(student_profile, course_group):
            raise ValidationError("Student is already enrolled in this course group.")
