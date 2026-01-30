from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from ..models import Course
from ..serializers import *
from ..permissions import AdminOrReadOnly
from ..services.courses import CourseService


COURSE_SERIALIZERS = {
    "admin": AdminCourseSerializer,
    "student": CourseSerializer,
}


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    permission_classes = [IsAuthenticated, AdminOrReadOnly]

    def get_serializer_class(self):
        role = getattr(self.request.user, "role", "student")
        return COURSE_SERIALIZERS.get(role, CourseSerializer)

    def perform_create(self, serializer):
        CourseService.save_course(serializer)

    def perform_update(self, serializer):
        CourseService.save_course(serializer)
