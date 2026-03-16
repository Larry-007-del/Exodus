import threading

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from attendance.models import Lecturer, Student
from attendance.notification_service import send_welcome_account_email


def _send_welcome_email(user_id, role):
    user = get_user_model().objects.filter(pk=user_id).first()
    if not user:
        return
    send_welcome_account_email(user, role=role)


def _queue_welcome_email(user_id, role):
    async_enabled = getattr(settings, 'SEND_WELCOME_EMAIL_ASYNC', not settings.DEBUG)
    if async_enabled:
        threading.Thread(
            target=_send_welcome_email,
            args=(user_id, role),
            daemon=True,
        ).start()
    else:
        _send_welcome_email(user_id, role)


@receiver(post_save, sender=Student)
def send_student_welcome_email(sender, instance, created, raw=False, **kwargs):
    if raw or not created:
        return
    if not instance.user_id:
        return
    transaction.on_commit(lambda user_id=instance.user_id: _queue_welcome_email(user_id, role='student'))


@receiver(post_save, sender=Lecturer)
def send_lecturer_welcome_email(sender, instance, created, raw=False, **kwargs):
    if raw or not created:
        return
    if not instance.user_id:
        return
    transaction.on_commit(lambda user_id=instance.user_id: _queue_welcome_email(user_id, role='lecturer'))
