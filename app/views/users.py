from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import User
from ..serializers import *
from ..permissions import RoleRequired
from ..validators import UserValidator


USER_SERIALIZERS = {
    "admin": AdminUserSerializer,
    "professor": ProfessorUserSerializer,
    "student": StudentUserSerializer,
}


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        role = getattr(self.request.user, "role", "admin")
        return USER_SERIALIZERS.get(role, AdminUserSerializer)

    def get_permissions(self):
        return [IsAuthenticated(), RoleRequired("admin")]

    def perform_create(self, serializer):
        UserValidator.validate_role_assignment(
            serializer.validated_data.get("role")
        )
        serializer.save()
