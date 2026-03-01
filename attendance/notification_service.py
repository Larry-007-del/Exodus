"""
Notification Service for Attendance System
Handles email and SMS notifications for students
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import Attendance, Student


def send_attendance_started_notifications(attendance, token):
    """
    Send notifications to students when an attendance session starts
    """
    course = attendance.course
    students = course.students.all()
    
    for student in students:
        # Send email notification if student wants it
        if student.should_send_email_notifications():
            send_attendance_started_email(student, course, token)
        
        # Send SMS notification if student wants it and has a phone number
        if student.should_send_sms_notifications():
            send_attendance_started_sms(student, course, token)


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
        print(f"Failed to send email to {student.user.email}: {str(e)}")
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
            print(f"Simulating SMS to {phone_number}: {message}")
        return True
    except Exception as e:
        print(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False


def send_attendance_expiring_notifications(attendance, token):
    """
    Send notifications to students when an attendance session is about to expire
    """
    course = attendance.course
    students = course.students.all()
    
    for student in students:
        if student not in attendance.present_students.all():
            if student.should_send_email_notifications():
                send_attendance_expiring_email(student, course, token, attendance)
            
            if student.should_send_sms_notifications():
                send_attendance_expiring_sms(student, course, token, attendance)


def send_attendance_expiring_email(student, course, token, attendance):
    """
    Send email notification for expiring attendance session
    """
    subject = f"Attendance Session Expiring Soon - {course.name}"
    expiration_time = attendance.created_at + timedelta(hours=4)
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
        print(f"Failed to send email to {student.user.email}: {str(e)}")
        return False


def send_attendance_expiring_sms(student, course, token, attendance):
    """
    Send SMS notification for expiring attendance session
    """
    expiration_time = attendance.created_at + timedelta(hours=4)
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
            print(f"Simulating SMS to {phone_number}: {message}")
        return True
    except Exception as e:
        print(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False


def send_attendance_missed_notifications(attendance):
    """
    Send notifications to students who missed an attendance session
    """
    course = attendance.course
    present_students = attendance.present_students.all()
    all_students = course.students.all()
    
    missed_students = [student for student in all_students if student not in present_students]
    
    for student in missed_students:
        if student.should_send_email_notifications():
            send_attendance_missed_email(student, course, attendance)
        
        if student.should_send_sms_notifications():
            send_attendance_missed_sms(student, course, attendance)


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
        print(f"Failed to send email to {student.user.email}: {str(e)}")
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
            print(f"Simulating SMS to {phone_number}: {message}")
        return True
    except Exception as e:
        print(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False