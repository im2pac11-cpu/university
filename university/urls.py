from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from app.views import (
    UserViewSet,
    CourseViewSet,
    CourseGroupViewSet,
    EnrollmentViewSet,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'groups', CourseGroupViewSet, basename='groups')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollments')

urlpatterns += router.urls
