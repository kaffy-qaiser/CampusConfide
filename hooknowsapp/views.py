from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, AnonymousUser
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Report, AdminNote, Notification
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from .forms import ReportForm
from .filters import ReportFilter


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/home')
    else:
        return render(request, 'hooknowsapp/login.html')


def home(request):
    notifications = None
    if not request.user.is_staff and not request.user.is_anonymous:
        notifications = Notification.objects.filter(user=request.user, read=False)
    return render(request, 'hooknowsapp/homepage.html', {'notifications': notifications})



def logout_view(request):
    logout(request)
    return redirect("/")


def create_report(request):
    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            if(request.user.is_anonymous):
                form.save()
                return render(request, 'hooknowsapp/report_submitted.html')
            else:
                report = form.save(commit=False)
                report.user = request.user
                report.save()
                return render(request, 'hooknowsapp/report_submitted.html')
    else:
        form = ReportForm()

    return render(request, 'hooknowsapp/create_report.html', {"form" : form})


def view_reports(request):
    reports = Report.objects.all()
    return render(request, 'hooknowsapp/view_reports.html', {'reports': reports})


def view_user_reports(request):
    user_id = request.user
    reports = Report.objects.filter(user_id=user_id)
    return render(request, 'hooknowsapp/view_reports.html', {'reports': reports})

def one_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)

    if request.user.is_staff:
        if report.submission_status == "New":
            report.submission_status = "In Progress"
            report.save()
            Notification.objects.create(user=report.user, report=report,
                                        message=f"Report {report_id} status has changed.")
    if not request.user.is_staff and not request.user.is_anonymous:
        notif = Notification.objects.filter(user=request.user, report=report, read=False)
        notif.update(read=True)
    return render(request, 'hooknowsapp/one_report.html', {'report': report})

@login_required
def report_resolved(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    if request.user.is_staff:
        if report.submission_status == "Resolved":
            report.submission_status = "In Progress"
            Notification.objects.create(user=report.user, report=report,
                                        message=f"Report {report_id} status has changed.")
        else:
            report.submission_status = "Resolved"
            Notification.objects.create(user=report.user, report=report,
                                        message=f"Report {report_id} has been resolved.")
        report.save()
    else:
        return HttpResponseForbidden("You do not have permission to perform this action.")
    return render(request, 'hooknowsapp/one_report.html', {'report': report})


def report_submitted(request):
    return render(request, 'hooknowsapp/report_submitted.html')

def add_admin_note(request, report_id):
    if request.method == "POST" and request.user.is_staff:
        report = get_object_or_404(Report, pk=report_id)
        note_content = request.POST.get('note', '')
        if note_content.strip():
            AdminNote.objects.create(report=report, note=note_content)
        return HttpResponseRedirect(reverse('one_report', args=[report_id]))
    else:
        return HttpResponseRedirect(reverse('home'))


@login_required
def delete_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.user == report.user and not request.user.is_staff:
        report.delete()
        return redirect('view_user_reports')
    else:
        return redirect('view_user_reports')

def report_list(request):
    reports = Report.objects.filter(user=request.user)
    report_filter = ReportFilter(request.GET, queryset=reports)
    filtered_reports = reports.order_by('created_at')

    if request.user.is_staff:
        reports = Report.objects.all()
        report_filter = ReportFilter(request.GET, queryset=reports)

    if 'search' in request.GET and request.GET.get('title'):
        filtered_reports = report_filter.qs

    return render(request, 'hooknowsapp/view_reports.html', {
        'filter': report_filter,
        'reports': filtered_reports,
    })
