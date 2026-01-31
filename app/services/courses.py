from django.db import transaction
from ..validators import CourseValidator


class CourseService:

    @staticmethod
    @transaction.atomic
    def save_course(serializer):
        units = serializer.validated_data.get("units")
        CourseValidator.validate_units(units)
        return serializer.save()
