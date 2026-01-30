from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import (
    StudentProfile,
    ProfessorProfile,
    Enrollment,
    CourseGroup,
)

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_sync_user_profile(sender, instance, created, **kwargs):
    if instance.role == User.Role.STUDENT:
        StudentProfile.objects.get_or_create(user=instance)

    elif instance.role == User.Role.PROFESSOR:
        ProfessorProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Enrollment)
def increase_registered_count(sender, instance, created, **kwargs):
    if created:
        CourseGroup.objects.filter(
            id=instance.course_group_id
        ).update(
            registered=models.F('registered') + 1
        )


@receiver(post_delete, sender=Enrollment)
def decrease_registered_count(sender, instance, **kwargs):
    CourseGroup.objects.filter(
        id=instance.course_group_id,
        registered__gt=0
    ).update(
        registered=models.F('registered') - 1
    )
