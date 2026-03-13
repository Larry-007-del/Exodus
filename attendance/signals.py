from django.db.models.signals import post_save
from django.dispatch import receiver

from attendance.models import Lecturer, Student
from attendance.notification_service import send_welcome_account_email


@receiver(post_save, sender=Student)
def send_student_welcome_email(sender, instance, created, raw=False, **kwargs):
    if raw or not created:
        return
    send_welcome_account_email(instance.user, role='student')


@receiver(post_save, sender=Lecturer)
def send_lecturer_welcome_email(sender, instance, created, raw=False, **kwargs):
    if raw or not created:
        return
    send_welcome_account_email(instance.user, role='lecturer')
