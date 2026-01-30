from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Course,
    Semester,
    CourseGroup,
    Enrollment,
    StudentProfile,
    ProfessorProfile
)

User = get_user_model()

class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "role")


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "password", "email", "role", "is_active")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfessorUserSerializer(BaseUserSerializer):
    professor_id = serializers.CharField(source="professor_profile.professor_id", read_only=True)


class StudentUserSerializer(BaseUserSerializer):
    student_id = serializers.CharField(source="student_profile.student_id", read_only=True)
    min_units = serializers.IntegerField(source="student_profile.min_units", read_only=True)
    max_units = serializers.IntegerField(source="student_profile.max_units", read_only=True)


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ("student_id", "min_units", "max_units")


class ProfessorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessorProfile
        fields = ("professor_id",)


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "code", "name", "units")


class AdminCourseSerializer(CourseSerializer):
    prerequisites = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        many=True,
        required=False
    )

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ("prerequisites",)


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ["id", "year", "term", "start_date", "end_date", "is_active"]


class AdminCourseGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseGroup
        fields = (
            "id",
            "course",
            "semester",
            "professor",
            "capacity",
            "registered",
            "day_of_week",
            "start_time",
            "end_time",
        )


class ProfessorCourseGroupSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)
    semester_name = serializers.SerializerMethodField()

    class Meta:
        model = CourseGroup
        fields = (
            "id",
            "course_name",
            "semester_name",
            "capacity",
            "registered",
            "day_of_week",
            "start_time",
            "end_time",
        )

    def get_semester_name(self, obj):
        return f"{obj.semester.year} - {obj.semester.get_term_display()}"


class StudentCourseGroupSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)
    professor_name = serializers.CharField(source="professor.username", read_only=True)
    semester_name = serializers.SerializerMethodField()

    class Meta:
        model = CourseGroup
        fields = (
            "id",
            "course_name",
            "professor_name",
            "semester_name",
            "day_of_week",
            "start_time",
            "end_time",
        )

    def get_semester_name(self, obj):
        return f"{obj.semester.year} - {obj.semester.get_term_display()}"


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.username", read_only=True)
    course_name = serializers.CharField(source="course_group.course.name", read_only=True)
    professor_name = serializers.CharField(source="course_group.professor.username", read_only=True)
    semester_name = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = (
            "id",
            "student",
            "student_name",
            "course_group",
            "course_name",
            "professor_name",
            "semester",
            "semester_name",
            "created_at",
        )

    def get_semester_name(self, obj):
        return f"{obj.semester.year} - {obj.semester.get_term_display()}"
