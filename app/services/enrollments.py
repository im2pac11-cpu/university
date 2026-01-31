from django.db import transaction
from ..validators import EnrollmentValidator


class EnrollmentService:

    @staticmethod
    @transaction.atomic
    def create(serializer):
        data = serializer.validated_data

        EnrollmentValidator.validate(
            data["student"],
            data["course_group"],
            data["semester"],
        )

        enrollment = serializer.save()

        course_group = data["course_group"]
        course_group.registered += 1
        course_group.save(update_fields=["registered"])

        return enrollment

    @staticmethod
    @transaction.atomic
    def update(serializer):
        data = serializer.validated_data

        EnrollmentValidator.validate(
            data["student"],
            data["course_group"],
            data["semester"],
        )

        return serializer.save()