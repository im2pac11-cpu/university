from rest_framework.exceptions import ValidationError

class CourseGroupValidator:

    @staticmethod
    def validate_capacity(capacity: int):
        if capacity <= 0:
            raise ValidationError("Course group capacity must be greater than 0.")

    @staticmethod
    def validate_times(start_time, end_time):
        if start_time >= end_time:
            raise ValidationError("Start time must be before end time.")
