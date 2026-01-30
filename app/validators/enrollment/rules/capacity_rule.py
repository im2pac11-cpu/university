from rest_framework.exceptions import ValidationError
from .base_rule import ValidationRule

class CapacityRule(ValidationRule):
    """Checks that the course group has not exceeded capacity."""

    def validate(self, student_profile, course_group, semester, repo):
        if course_group.registered >= course_group.capacity:
            raise ValidationError("Cannot enroll: course group capacity exceeded.")
