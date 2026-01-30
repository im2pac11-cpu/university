from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import Enrollment
from ..serializers import EnrollmentSerializer
from ..permissions import RoleRequired
from ..policies.enrollments import ENROLLMENT_POLICIES
from ..services.enrollments import EnrollmentService


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        role = getattr(self.request.user, "role", "student")
        policy = ENROLLMENT_POLICIES.get(role)
        return policy.get_queryset(self.request.user)

    def get_permissions(self):
        return [IsAuthenticated(), RoleRequired(getattr(self.request.user, "role", "student"))]

    def perform_create(self, serializer):
        EnrollmentService.create(serializer)

    def perform_update(self, serializer):
        EnrollmentService.update(serializer)