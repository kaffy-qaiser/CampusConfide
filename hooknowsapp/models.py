from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Report(models.Model):
    submission_types = (
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    )
    ISSUE_TYPES = (
        ('professors', 'Professors'),
        ('teaching_assistant', 'Teaching Assistant'),
        ('homework_assignments', 'Homework Assignments'),
        ('course_logistics', 'Course Logistics'),
        ('tests_exams', 'Tests/Exams'),
        ('others', 'Others'),
    )
    issue_type = models.CharField(
        max_length=30, 
        choices=ISSUE_TYPES, 
        default='others',
        verbose_name="Related to"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(default='', max_length=200)
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    submission_status = models.CharField(max_length=30, choices=submission_types, default='New')

 
class AdminNote(models.Model):
    report = models.ForeignKey(Report, related_name='admin_notes', on_delete=models.CASCADE)
    note = models.TextField()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, blank=True, null=True)
    message = models.TextField(default='', max_length=200)
    read = models.BooleanField(default=False)
