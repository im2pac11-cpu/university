from rest_framework.exceptions import ValidationError

class CourseValidator:
    MAX_UNITS = 10

    @staticmethod
    def validate_units(units: int):
        if units <= 0:
            raise ValidationError("Course units must be greater than 0.")
        if units > CourseValidator.MAX_UNITS:
            raise ValidationError(f"Course units cannot exceed {CourseValidator.MAX_UNITS}.")
