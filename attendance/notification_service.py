"""
Notification Service for Attendance System
Handles email, SMS, and Firebase Cloud Messaging (FCM) push notifications for students.
"""
import json
import logging

from django.core.mail import send_mail, get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import Attendance, Student

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Firebase / FCM helpers
# ---------------------------------------------------------------------------

_firebase_app = None  # lazily initialised


def _get_firebase_app():
    """Return the default Firebase Admin app, initialising it on first call.

    Reads FIREBASE_SERVICE_ACCOUNT_JSON from settings (env var).  Returns
    None if the env var is absent so callers can safely skip FCM.
    """
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    service_account_json = getattr(settings, 'FIREBASE_SERVICE_ACCOUNT_JSON', None)
    if not service_account_json:
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials

        # Avoid re-initialising if already initialised in a different code path
        try:
            _firebase_app = firebase_admin.get_app()
        except ValueError:
            service_account_dict = (
                json.loads(service_account_json)
                if isinstance(service_account_json, str)
                else service_account_json
            )
            cred = credentials.Certificate(service_account_dict)
            _firebase_app = firebase_admin.initialize_app(cred)

    except ImportError:
        logger.warning("firebase_admin not installed — FCM push notifications disabled.")
    except Exception as exc:
        logger.error("Failed to initialise Firebase Admin SDK: %s", exc)

    return _firebase_app


def send_push_notification(fcm_token, title, body, data=None):
    """Send a single FCM push notification to a device token.

    Args:
        fcm_token: The device FCM registration token string.
        title:     Notification title.
        body:      Notification body text.
        data:      Optional dict of string key/value pairs for the data payload.

    Returns:
        True on success, False on failure / not configured.
    """
    if not fcm_token:
        return False

    app = _get_firebase_app()
    if app is None:
        logger.debug("FCM not configured — skipping push to token ending …%s", fcm_token[-6:])
        return False

    try:
        from firebase_admin import messaging

        notification = messaging.Notification(title=title, body=body)
        message = messaging.Message(
            notification=notification,
            data={str(k): str(v) for k, v in (data or {}).items()},
            token=fcm_token,
        )
        response = messaging.send(message, app=app)
        logger.info("FCM push sent: %s (token …%s)", response, fcm_token[-6:])
        return True
    except Exception as exc:
        logger.error("FCM push failed for token …%s: %s", fcm_token[-6:], exc)
        return False


def send_bulk_push_notifications(tokens_and_targets, title, body, data=None):
    """Send FCM push to multiple tokens via the Multicast API (up to 500 at once).

    Args:
        tokens_and_targets: iterable of FCM token strings (None/empty values are skipped).
        title, body, data:  same as send_push_notification.
    """
    app = _get_firebase_app()
    if app is None:
        return

    valid_tokens = [t for t in tokens_and_targets if t]
    if not valid_tokens:
        return

    try:
        from firebase_admin import messaging

        # FCM Multicast supports up to 500 tokens per call
        BATCH = 500
        for i in range(0, len(valid_tokens), BATCH):
            batch_tokens = valid_tokens[i: i + BATCH]
            mm = messaging.MulticastMessage(
                notification=messaging.Notification(title=title, body=body),
                data={str(k): str(v) for k, v in (data or {}).items()},
                tokens=batch_tokens,
            )
            resp = messaging.send_each_for_multicast(mm, app=app)
            logger.info(
                "FCM multicast: %d success, %d failure (batch %d–%d)",
                resp.success_count, resp.failure_count, i, i + len(batch_tokens),
            )
    except Exception as exc:
        logger.error("FCM multicast failed: %s", exc)




def send_welcome_account_email(user, role='student'):
    """Send onboarding email when a Student/Lecturer profile is created."""
    if not user or not user.email:
        return False

    role_label = 'Lecturer' if role == 'lecturer' else 'Student'
    subject = f"Welcome to Exodus - {role_label} Account"
    context = {
        'user': user,
        'role': role_label,
        'login_url': '/login/',
    }
    html_message = render_to_string('emails/welcome_account.html', context)
    plain_message = (
        f"Welcome to Exodus, {user.username}! "
        f"Your {role_label.lower()} account is ready. "
        f"Sign in at {context['login_url']} to get started."
    )

    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error("Failed to send welcome email to %s: %s", user.email, e)
        return False


def send_attendance_started_notifications(attendance, token):
    """
    Send notifications to students when an attendance session starts.
    Dispatches email, SMS, and FCM push concurrently.
    """
    course = attendance.course
    students = course.students.select_related('user').all()

    emails_to_send = []
    fcm_tokens = []

    for student in students:
        # Email
        if student.should_send_email_notifications():
            subject = f"Attendance Session Started - {course.name}"
            context = {'student': student, 'course': course, 'token': token}
            html_message = render_to_string('emails/attendance_started.html', context)
            plain_message = f"Attendance session started for {course.name} ({course.course_code}). Token: {token}"
            msg = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [student.user.email])
            msg.attach_alternative(html_message, "text/html")
            emails_to_send.append(msg)

        # SMS
        if student.should_send_sms_notifications():
            send_attendance_started_sms(student, course, token)

        # FCM push (collect token for bulk dispatch)
        if student.fcm_token:
            fcm_tokens.append(student.fcm_token)

    if emails_to_send:
        try:
            connection = get_connection()
            connection.send_messages(emails_to_send)
        except Exception as e:
            logger.error("Failed to send bulk started emails: %s", e)

    # Send push notifications to all enrolled students at once
    send_bulk_push_notifications(
        fcm_tokens,
        title=f"Attendance Started – {course.course_code}",
        body=f"Session started for {course.name}. Token: {token}",
        data={'course_code': course.course_code, 'token': str(token), 'type': 'started'},
    )

def send_attendance_started_email(student, course, token):
    """
    Send email notification for started attendance session
    """
    subject = f"Attendance Session Started - {course.name}"
    context = {
        'student': student,
        'course': course,
        'token': token,
    }
    
    html_message = render_to_string('emails/attendance_started.html', context)
    plain_message = f"Attendance session started for {course.name} ({course.course_code}). Token: {token}"
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [student.user.email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", student.user.email, e)
        return False


def send_attendance_started_sms(student, course, token):
    """
    Send SMS notification for started attendance session
    """
    message = f"Attendance session started for {course.course_code}. Token: {token}"
    phone_number = student.phone_number
    
    try:
        # Try to send SMS using Twilio if configured
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
        # Try to send SMS using Africa's Talking if configured
        elif settings.AFRICAS_TALKING_USERNAME and settings.AFRICAS_TALKING_API_KEY:
            import africastalking
            africastalking.initialize(settings.AFRICAS_TALKING_USERNAME, settings.AFRICAS_TALKING_API_KEY)
            sms = africastalking.SMS
            sms.send(message, [phone_number])
        else:
            # Fallback to simulation if no SMS service configured
            logger.info("Simulating SMS to %s: %s", phone_number, message)
        return True
    except ImportError as e:
        logger.warning("SMS package not installed (pip install twilio / africastalking): %s", e)
        return False
    except Exception as e:
        logger.error("Failed to send SMS to %s: %s", phone_number, e)
        return False


def send_attendance_expiring_notifications(attendance, token):
    """
    Send notifications to absent students when an attendance session is about to expire.
    Dispatches email, SMS, and FCM push to students who haven't checked in yet.
    """
    course = attendance.course
    students = course.students.select_related('user').all()
    present_ids = set(attendance.present_students.values_list('id', flat=True))
    duration_hours = attendance.duration_hours or 2
    expiration_time = attendance.created_at + timedelta(hours=duration_hours)

    emails_to_send = []
    fcm_tokens = []

    for student in students:
        if student.id not in present_ids:
            # Email
            if student.should_send_email_notifications():
                subject = f"Attendance Session Expiring Soon - {course.name}"
                context = {
                    'student': student,
                    'course': course,
                    'token': token,
                    'expiration_time': expiration_time.strftime('%H:%M:%S'),
                }
                html_message = render_to_string('emails/attendance_expiring.html', context)
                plain_message = f"Attendance session for {course.course_code} expires in 15 minutes. Token: {token}"
                msg = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [student.user.email])
                msg.attach_alternative(html_message, "text/html")
                emails_to_send.append(msg)

            # SMS
            if student.should_send_sms_notifications():
                send_attendance_expiring_sms(student, course, token, attendance)

            # FCM push
            if student.fcm_token:
                fcm_tokens.append(student.fcm_token)

    if emails_to_send:
        try:
            connection = get_connection()
            connection.send_messages(emails_to_send)
        except Exception as e:
            logger.error("Failed to send bulk expiring emails: %s", e)

    send_bulk_push_notifications(
        fcm_tokens,
        title=f"Attendance Expiring \u2013 {course.course_code}",
        body=f"Session closes at {expiration_time.strftime('%H:%M')}. Token: {token}",
        data={'course_code': course.course_code, 'token': str(token), 'type': 'expiring'},
    )


def send_attendance_expiring_email(student, course, token, attendance):
    """
    Send email notification for expiring attendance session
    """
    subject = f"Attendance Session Expiring Soon - {course.name}"
    duration_hours = attendance.duration_hours or 2
    expiration_time = attendance.created_at + timedelta(hours=duration_hours)
    context = {
        'student': student,
        'course': course,
        'token': token,
        'expiration_time': expiration_time.strftime('%H:%M:%S')
    }
    
    html_message = render_to_string('emails/attendance_expiring.html', context)
    plain_message = f"Attendance session for {course.course_code} expires in 15 minutes. Token: {token}"
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [student.user.email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        logger.error("Failed to send expiring email to %s: %s", student.user.email, e)
        return False


def send_attendance_expiring_sms(student, course, token, attendance):
    """
    Send SMS notification for expiring attendance session
    """
    duration_hours = attendance.duration_hours or 2
    expiration_time = attendance.created_at + timedelta(hours=duration_hours)
    message = f"Attendance for {course.course_code} expires in 15 minutes. Token: {token}"
    phone_number = student.phone_number
    
    try:
        # Try to send SMS using Twilio if configured
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
        # Try to send SMS using Africa's Talking if configured
        elif settings.AFRICAS_TALKING_USERNAME and settings.AFRICAS_TALKING_API_KEY:
            import africastalking
            africastalking.initialize(settings.AFRICAS_TALKING_USERNAME, settings.AFRICAS_TALKING_API_KEY)
            sms = africastalking.SMS
            sms.send(message, [phone_number])
        else:
            # Fallback to simulation if no SMS service configured
            logger.info("Simulating SMS to %s: %s", phone_number, message)
        return True
    except ImportError as e:
        logger.warning("SMS package not installed (pip install twilio / africastalking): %s", e)
        return False
    except Exception as e:
        logger.error("Failed to send SMS to %s: %s", phone_number, e)
        return False


def send_attendance_missed_notifications(attendance):
    """
    Send notifications to students who missed an attendance session.
    Dispatches email, SMS, and FCM push to all absent students.
    """
    course = attendance.course
    present_ids = set(attendance.present_students.values_list('id', flat=True))
    all_students = course.students.select_related('user').all()

    missed_students = [s for s in all_students if s.id not in present_ids]

    emails_to_send = []
    fcm_tokens = []

    for student in missed_students:
        # Email
        if student.should_send_email_notifications():
            subject = f"You Missed Attendance - {course.name}"
            context = {
                'student': student,
                'course': course,
                'session_date': attendance.date.strftime('%Y-%m-%d'),
            }
            html_message = render_to_string('emails/attendance_missed.html', context)
            plain_message = f"You missed the attendance session for {course.course_code} on {attendance.date}"
            msg = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [student.user.email])
            msg.attach_alternative(html_message, "text/html")
            emails_to_send.append(msg)

        # SMS
        if student.should_send_sms_notifications():
            send_attendance_missed_sms(student, course, attendance)

        # FCM push
        if student.fcm_token:
            fcm_tokens.append(student.fcm_token)

    if emails_to_send:
        try:
            connection = get_connection()
            connection.send_messages(emails_to_send)
        except Exception as e:
            logger.error("Failed to send bulk missed emails: %s", e)

    send_bulk_push_notifications(
        fcm_tokens,
        title=f"Attendance Missed \u2013 {course.course_code}",
        body=f"You missed the {course.name} session on {attendance.date}.",
        data={'course_code': course.course_code, 'session_date': str(attendance.date), 'type': 'missed'},
    )

def send_attendance_missed_email(student, course, attendance):
    """
    Send email notification for missed attendance session
    """
    subject = f"You Missed Attendance - {course.name}"
    context = {
        'student': student,
        'course': course,
        'session_date': attendance.date.strftime('%Y-%m-%d')
    }
    
    html_message = render_to_string('emails/attendance_missed.html', context)
    plain_message = f"You missed the attendance session for {course.course_code} on {attendance.date}"
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [student.user.email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        logger.error("Failed to send missed email to %s: %s", student.user.email, e)
        return False


def send_attendance_missed_sms(student, course, attendance):
    """
    Send SMS notification for missed attendance session
    """
    message = f"You missed the attendance session for {course.course_code} on {attendance.date}"
    phone_number = student.phone_number
    
    try:
        # Try to send SMS using Twilio if configured
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
        # Try to send SMS using Africa's Talking if configured
        elif settings.AFRICAS_TALKING_USERNAME and settings.AFRICAS_TALKING_API_KEY:
            import africastalking
            africastalking.initialize(settings.AFRICAS_TALKING_USERNAME, settings.AFRICAS_TALKING_API_KEY)
            sms = africastalking.SMS
            sms.send(message, [phone_number])
        else:
            # Fallback to simulation if no SMS service configured
            logger.info("Simulating SMS to %s: %s", phone_number, message)
        return True
    except ImportError as e:
        logger.warning("SMS package not installed (pip install twilio / africastalking): %s", e)
        return False
    except Exception as e:
        logger.error("Failed to send SMS to %s: %s", phone_number, e)
        return False