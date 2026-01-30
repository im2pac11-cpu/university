from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import CourseGroup, StudentProfile
from ..serializers import *
from ..permissions import RoleRequired
from ..policies.course_groups import COURSE_GROUP_POLICIES
from ..services.course_groups import CourseGroupService


COURSE_GROUP_SERIALIZERS = {
    "admin": AdminCourseGroupSerializer,
    "professor": ProfessorCourseGroupSerializer,
    "student": StudentCourseGroupSerializer,
}


class CourseGroupViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter]
    search_fields = ["course__name", "professor__username"]

    def get_queryset(self):
        role = getattr(self.request.user, "role", "student")
        policy = COURSE_GROUP_POLICIES.get(role)
        return policy.get_queryset(self.request.user)

    def get_serializer_class(self):
        role = getattr(self.request.user, "role", "student")
        return COURSE_GROUP_SERIALIZERS.get(role, StudentCourseGroupSerializer)

    def get_permissions(self):
        return [IsAuthenticated(), RoleRequired(getattr(self.request.user, "role", "student"))]

    def perform_create(self, serializer):
        CourseGroupService.save_group(serializer)

    def perform_update(self, serializer):
        CourseGroupService.save_group(serializer)

    @action(detail=False, methods=["get"], permission_classes=[RoleRequired("student")])
    def my_courses(self, request):
        student = getattr(request.user, "student_profile", None)
        if not student:
            return Response({"detail": "Student profile not found"}, status=404)

        queryset = CourseGroup.objects.filter(
            enrollments__student=student,
            semester__is_active=True,
        )

        return Response(StudentCourseGroupSerializer(queryset, many=True).data)