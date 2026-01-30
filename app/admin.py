from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    User,
    StudentProfile,
    ProfessorProfile,
    Course,
    Semester,
    CourseGroup,
    Enrollment
)


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    extra = 0


class ProfessorProfileInline(admin.StackedInline):
    model = ProfessorProfile
    can_delete = False
    extra = 0

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("username", "email")
    ordering = ("username",)

    fieldsets = (
        ("Account", {
            "fields": ("username", "password")
        }),
        ("Personal info", {
            "fields": ("email",)
        }),
        ("Role", {
            "fields": ("role",)
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2", "role"),
        }),
    )

    def get_inlines(self, request, obj=None):
        """
        Show inline profile based on role
        (OCP + SRP ✔)
        """
        if not obj:
            return []

        if obj.role == User.Role.STUDENT:
            return [StudentProfileInline]

        if obj.role == User.Role.PROFESSOR:
            return [ProfessorProfileInline]

        return []


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "units")
    search_fields = ("code", "name")
    filter_horizontal = ("prerequisites",)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('year', 'term', 'start_date', 'end_date', 'is_active')
    list_filter = ('year', 'term', 'is_active')


@admin.register(CourseGroup)
class CourseGroupAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "semester",
        "professor",
        "capacity",
        "registered",
        "day_of_week",
        "start_time",
        "end_time",
    )

    list_filter = ("semester",)
    search_fields = ("course__name", "professor__username")

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course_group",
        "semester",
        "created_at",
        "min_units_warning",
    )

    list_filter = ("semester",)
    search_fields = ("student__username",)

    def min_units_warning(self, obj):
        """
        نمایش هشدار اگر مجموع واحدهای ثبت‌نام شده کمتر از حداقل واحد دانشجو باشد.
        """
        student = obj.student
        total_units = sum(
            e.course_group.course.units
            for e in Enrollment.objects.filter(student=student)
        )
        if total_units < student.min_units:
            return f"⚠ Student below minimum units ({total_units}/{student.min_units})"
        return "-"
    
    min_units_warning.short_description = "Min Units Warning"
    min_units_warning.admin_order_field = None
