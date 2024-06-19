from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Report, Notification, AdminNote
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import ReportForm
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hooknows.settings')
django.setup()

# Testing Views

class TestLogIn(TestCase):
    def test_login(self):
        self.user = User.objects.create_user(username='user', password="pass")
        login_successful = self.client.login(username='user', password='pass')
        self.assertTrue(login_successful)

        response = self.client.get(reverse('login'), follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse('home'))


class TestReport(TestCase):
    def setUp(self):
        # Create a user if authentication is required for these views
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_view_report_submitted(self):
        response = self.client.get(reverse('create_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hooknowsapp/create_report.html')

    def test_view_reports(self):
        response = self.client.get(reverse('view_reports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hooknowsapp/view_reports.html')

    def test_create_report(self):
        report_data = {
            'title': 'New Report',
            'description': 'Description of the new report'
        }
        response = self.client.post(reverse('create_report'), report_data)

        response = self.client.get(reverse('view_reports'))
        self.assertEqual(response.status_code, 200)


class TestHomeViews(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home') 
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        
    def test_anonymous(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hooknowsapp/homepage.html')
        self.assertIsNone(response.context['notifications'])  

    def test_staff(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hooknowsapp/homepage.html')
        self.assertIsNone(response.context['notifications']) 

    def test_user_wo_notifications(self):
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hooknowsapp/homepage.html')
        self.assertEqual(list(response.context['notifications']), [])  

    def test_user_notifications(self):
        self.client.login(username='testuser', password='testpassword')
        notification = Notification.objects.create(user=self.user, read=False, message='Test Notification')
        
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hooknowsapp/homepage.html')
        self.assertIn(notification, response.context['notifications']) 
    
class TestLogoutView(TestCase):
    
    def test_logout(self):
        self.client = Client()
        self.logout_url = reverse('logout')  
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, '/', status_code=302)
        self.assertNotIn('_auth_user_id', self.client.session)


class TestReportView(TestCase):
    def setUp(self):
        self.client = Client()
        self.view_reports_url = reverse('view_reports')  
        
        Report.objects.create(title='Report 1', description='Content for report 1')
        Report.objects.create(title='Report 2', description='Content for report 2')

    def test_view_reports(self):
        response = self.client.get(self.view_reports_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hooknowsapp/view_reports.html')
        
        reports_in_context = response.context['reports']
        self.assertEqual(reports_in_context.count(), 2)
        report_titles = reports_in_context.values_list('title', flat=True)
        self.assertIn('Report 1', report_titles)
        self.assertIn('Report 2', report_titles)


class TestUserReportView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.other_user = User.objects.create_user(username='otheruser', password='testpassword')
        self.view_user_reports_url = reverse('view_user_reports')  
        
        Report.objects.create(user=self.user, title='User Report 1', description='Content for user report 1')
        Report.objects.create(user=self.user, title='User Report 2', description='Content for user report 2')
        Report.objects.create(user=self.other_user, title='Other User Report', description='Content for other user report')

    def test_view_user_reports_response(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.view_user_reports_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hooknowsapp/view_reports.html')
        
    def test_view_user_reports_counts(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.view_user_reports_url)
        reports_in_context = response.context['reports']
        self.assertEqual(reports_in_context.count(), 2)
        
        for report in reports_in_context:
            self.assertEqual(report.user, self.user)
        self.assertTrue(any(report.title == 'User Report 1' for report in reports_in_context))
        self.assertTrue(any(report.title == 'User Report 2' for report in reports_in_context))
        self.assertFalse(any(report.title == 'Other User Report' for report in reports_in_context))

    def test_different_user(self):
        self.client.login(username='otheruser', password='testpassword')
        response = self.client.get(self.view_user_reports_url)
        self.assertEqual(response.status_code, 200)
        reports_in_context = response.context['reports']
        self.assertFalse(any(report.user == self.user for report in reports_in_context))


class TestOneReportView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user', password='password')
        self.staff_user = User.objects.create_user(username='staff', password='password', is_staff=True)
        self.report = Report.objects.create(user=self.user, title='User Report', description='A report')
        self.one_report_url = reverse('one_report', kwargs={'report_id': self.report.pk})
        self.report_resolved_url = reverse('report_resolved', kwargs={'report_id': self.report.pk})

        
    def test_one_report_view_by_staff_changes_status(self):
        self.client.login(username='staff', password='password')
        response = self.client.get(self.one_report_url)
        self.report.refresh_from_db()
        self.assertEqual(self.report.submission_status, 'In Progress')
        self.assertTrue(Notification.objects.filter(user=self.user, report=self.report).exists())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hooknowsapp/one_report.html')

    def test_one_report_view_by_user_marks_notifications(self):
        Notification.objects.create(user=self.user, report=self.report, message='Test Notification', read=False)
        self.client.login(username='user', password='password')
        response = self.client.get(self.one_report_url)
        
        self.assertEqual(Notification.objects.filter(user=self.user, report=self.report, read=True).count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hooknowsapp/one_report.html')

    def test_one_report_view_not_found(self):
        wrong_report_url = reverse('one_report', kwargs={'report_id': 999})
        self.client.login(username='user', password='password')
        response = self.client.get(wrong_report_url)
        self.assertEqual(response.status_code, 404)

    def test_report_resolved_by_staff(self):
        self.client.login(username='staff', password='password')
        self.assertNotEqual(self.report.submission_status, 'Resolved')

        response = self.client.get(self.report_resolved_url)
        self.report.refresh_from_db()
        self.assertEqual(self.report.submission_status, 'Resolved')
        self.assertTrue(Notification.objects.filter(user=self.report.user, report=self.report).exists())
        self.assertTemplateUsed(response, 'hooknowsapp/one_report.html')

    def test_report_resolved_toggle_by_staff(self):
        self.report.submission_status = 'Resolved'
        self.report.save()
        self.client.login(username='staff', password='password')
        response = self.client.get(self.report_resolved_url)
        self.report.refresh_from_db()
        self.assertEqual(self.report.submission_status, 'In Progress')
        self.assertTrue(Notification.objects.filter(user=self.report.user, report=self.report, message=f"Report {self.report.pk} status has changed.").exists())
        self.assertTemplateUsed(response, 'hooknowsapp/one_report.html')

    def test_report_resolved_access_by_regular_user(self):
        self.client.login(username='user', password='password')
        response = self.client.get(self.report_resolved_url)
        self.assertEqual(response.status_code, 403) 

class TestReportViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', 'user@test.com', 'password')
        self.staff_user = User.objects.create_user('staff', 'staff@test.com', 'staffpassword', is_staff=True)
        
        self.report = Report.objects.create(
            user=self.user, 
            title='Test Report', 
            description='Test Description', 
            submission_status='New'
        )
        
        self.report_submitted_url = reverse('report_submitted')
        
        self.report_resolved_url = reverse('report_resolved', args=[self.report.pk])

    def test_report_submitted_view(self):
        self.client.login(username='user', password='password')
        response = self.client.get(self.report_submitted_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hooknowsapp/report_submitted.html')

    def test_report_resolved_by_staff(self):
        self.client.login(username='staff', password='staffpassword')
        response = self.client.post(self.report_resolved_url)
        self.assertEqual(response.status_code, 200)
        self.report.refresh_from_db()
        self.assertEqual(self.report.submission_status, 'Resolved')
        self.assertTemplateUsed(response, 'hooknowsapp/one_report.html')
        self.assertTrue(Notification.objects.filter(user=self.user, report=self.report).exists())

    def test_report_resolved_access_by_regular_user(self):
        self.client.login(username='user', password='password')
        response = self.client.post(self.report_resolved_url)
        self.assertEqual(response.status_code, 403)

    def test_toggle_report_status_by_staff(self):
        self.report.submission_status = 'Resolved'
        self.report.save()

        self.client.login(username='staff', password='staffpassword')
        response = self.client.post(self.report_resolved_url)
        self.report.refresh_from_db()
        self.assertEqual(self.report.submission_status, 'In Progress')
        self.assertTrue(Notification.objects.filter(user=self.user, report=self.report).exists())



class TestAdminNote(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', 'user@test.com', 'password')
        self.staff_user = User.objects.create_user('staff', 'staff@test.com', 'staffpassword', is_staff=True)
        
        self.report = Report.objects.create(
            user=self.user, 
            title='Test Report', 
            description='Test Description', 
            submission_status='New'
        )
        
        self.add_admin_note_url = reverse('add_admin_note', args=[self.report.pk])
        self.one_report_url = reverse('one_report', args=[self.report.pk])
        self.home_url = reverse('home')

    def test_add_admin_note_by_staff(self):
        self.client.login(username='staff', password='staffpassword')
        note_content = 'This is an admin note.'
        response = self.client.post(self.add_admin_note_url, {'note': note_content})
        self.assertRedirects(response, self.one_report_url, status_code=302)

        self.assertTrue(AdminNote.objects.filter(report=self.report, note=note_content).exists())

    def test_add_admin_note_by_non_staff(self):
        self.client.login(username='user', password='password')
        note_content = 'This note should not be created.'
        response = self.client.post(self.add_admin_note_url, {'note': note_content})
        self.assertRedirects(response, self.home_url, status_code=302)

        self.assertFalse(AdminNote.objects.filter(report=self.report, note=note_content).exists())

    def test_add_admin_note_invalid_method(self):
        self.client.login(username='staff', password='staffpassword')
        response = self.client.get(self.add_admin_note_url)
        self.assertRedirects(response, self.home_url, status_code=302)

#Testing models

class TestReportModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_create_report(self):
        report = Report.objects.create(
            user=self.user,
            title="Test Report",
            description="A detailed description.",
            file='path/to/testfile.txt',
            submission_status='new'
        )

        self.assertEqual(report.title, "Test Report")
        self.assertEqual(report.description, "A detailed description.")
        self.assertEqual(report.submission_status, 'new')
        self.assertIsNotNone(report.created_at)  

    def test_submission_status_choices(self):
        report = Report.objects.create(
            user=self.user,
            title="Test Report",
            description="Testing choices.",
            submission_status='resolved'
        )
        self.assertIn(report.submission_status, dict(Report.submission_types).keys())

class TestAdminNoteModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.report = Report.objects.create(
            user=self.user,
            title="Test Report",
            description="A detailed description."
        )

    def test_create_admin_note(self):
        admin_note = AdminNote.objects.create(
            report=self.report,
            note="This is an admin note."
        )

        self.assertEqual(admin_note.note, "This is an admin note.")
        self.assertEqual(admin_note.report, self.report)

class NotificationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.report = Report.objects.create(
            user=self.user,
            title="Test Report"
        )

    def test_create_notification(self):
        notification = Notification.objects.create(
            user=self.user,
            report=self.report,
            message="You have a new notification."
        )

        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.report, self.report)
        self.assertEqual(notification.message, "You have a new notification.")
        self.assertFalse(notification.read)  
