from django.contrib import admin
from django.urls import path, include, re_path
from hooknowsapp import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('create_report/', views.create_report, name='create_report'),
    path('view_reports/', views.view_reports, name='view_reports'),
    path('report_submited/', views.report_submitted, name='report_submitted'),
    path('one_report/<int:report_id>/', views.one_report, name='one_report'),
    path('view_user_reports/', views.view_user_reports, name='view_user_reports'),
    path('add_admin_note/<int:report_id>/', views.add_admin_note, name='add_admin_note'),
    path('report_resolved/<int:report_id>/', views.report_resolved, name='report_resolved'),
    path('report/<int:report_id>/delete/', views.delete_report, name='delete_report'),
    path('reports/', views.report_list, name='report_list'),
    re_path(r'^search/$', views.report_list, name='search'),
]