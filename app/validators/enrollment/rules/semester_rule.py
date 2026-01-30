from rest_framework.exceptions import ValidationError
from .base_rule import ValidationRule

class SemesterActiveRule(ValidationRule):
    """Checks that the semester is active."""

    def validate(self, student_profile, course_group, semester, repo):
        if not semester.is_active:
            raise ValidationError("Cannot enroll in an inactive semester.")
