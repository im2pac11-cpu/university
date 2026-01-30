from rest_framework.exceptions import ValidationError
from .base_rule import ValidationRule

class TotalUnitsRule(ValidationRule):
    """Checks that the student’s total units are within allowed min/max."""

    def validate(self, student_profile, course_group, semester, repo):
        errors = []
        warnings = []

        current_units = repo.total_units(student_profile)
        total_units = current_units + course_group.course.units

        if total_units < student_profile.min_units:
            warnings.append("Student has not reached minimum units.")
        if total_units > student_profile.max_units:
            errors.append("Total enrolled units exceed student's maximum units.")

        if errors:
            raise ValidationError({"non_field_errors": errors})

        return {"warnings": warnings}
