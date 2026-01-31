from django.db import transaction
from ..validators import UserValidator
from ..models import StudentProfile


class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(serializer):
        role = serializer.validated_data.get("role")

        # Domain rule
        UserValidator.validate_role_assignment(role)

        user = serializer.save()

        # Side effects based on role
        if role == "student":
            StudentProfile.objects.create(user=user)

        return user
