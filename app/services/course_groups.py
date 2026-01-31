from django.db import transaction
from ..validators import CourseGroupValidator


class CourseGroupService:

    @staticmethod
    @transaction.atomic
    def save_group(serializer):
        data = serializer.validated_data

        CourseGroupValidator.validate_capacity(data["capacity"])
        CourseGroupValidator.validate_times(
            data["start_time"],
            data["end_time"],
        )

        return serializer.save()