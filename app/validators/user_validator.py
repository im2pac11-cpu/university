from rest_framework.exceptions import ValidationError

class UserValidator:
    VALID_ROLES = ["admin", "professor", "student"]

    @staticmethod
    def validate_role(role: str):
        if role not in UserValidator.VALID_ROLES:
            raise ValidationError(
                f"Invalid role: {role}. Must be one of {UserValidator.VALID_ROLES}"
            )
