import json
from datetime import timedelta

from django import template
from django.core.cache import cache
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

register = template.Library()


@register.inclusion_tag('admin/exodus_stats.html')
def exodus_dashboard_stats():
    """Render attendance system stats cards on the admin dashboard."""
    from attendance.models import Student, Lecturer, Course, Attendance, AttendanceStudent

    cache_key = 'exodus_admin_dashboard_analytics_v1'
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    today = timezone.now().date()
    start_day = today - timedelta(days=6)

    attendance_by_day_qs = (
        Attendance.objects.filter(date__gte=start_day, date__lte=today)
        .annotate(day=TruncDate('date'))
        .values('day')
        .annotate(total=Count('id'))
    )
    checkins_by_day_qs = (
        AttendanceStudent.objects.filter(marked_at__date__gte=start_day, marked_at__date__lte=today)
        .annotate(day=TruncDate('marked_at'))
        .values('day')
        .annotate(total=Count('id'))
    )

    attendance_by_day = {item['day']: item['total'] for item in attendance_by_day_qs}
    checkins_by_day = {item['day']: item['total'] for item in checkins_by_day_qs}

    labels = []
    session_trend = []
    checkin_trend = []
    for day_offset in range(7):
        day = start_day + timedelta(days=day_offset)
        labels.append(day.strftime('%a'))
        session_trend.append(attendance_by_day.get(day, 0))
        checkin_trend.append(checkins_by_day.get(day, 0))

    peak_value = max(session_trend + checkin_trend) if (session_trend or checkin_trend) else 0
    week_rows = []
    for index, label in enumerate(labels):
        session_value = session_trend[index]
        checkin_value = checkin_trend[index]
        week_rows.append({
            'label': label,
            'sessions': session_value,
            'checkins': checkin_value,
            'session_percent': int((session_value / peak_value) * 100) if peak_value else 0,
            'checkin_percent': int((checkin_value / peak_value) * 100) if peak_value else 0,
        })

    data = {
        'total_students': Student.objects.count(),
        'total_lecturers': Lecturer.objects.count(),
        'active_courses': Course.objects.filter(is_active=True).count(),
        'total_checkins': AttendanceStudent.objects.count(),
        'active_sessions': Attendance.objects.filter(is_active=True).count(),
        'today_sessions': Attendance.objects.filter(date=today).count(),
        'session_trend_labels_json': json.dumps(labels),
        'session_trend_values_json': json.dumps(session_trend),
        'checkin_trend_values_json': json.dumps(checkin_trend),
        'week_sessions_total': sum(session_trend),
        'week_checkins_total': sum(checkin_trend),
        'week_peak_sessions': max(session_trend) if session_trend else 0,
        'week_rows': week_rows,
    }

    cache.set(cache_key, data, 300)
    return data
