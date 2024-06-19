from django import forms
from .models import Report
import django_filters

class ReportFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    submission_status = django_filters.MultipleChoiceFilter(choices=Report.submission_types,
                                                            widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = Report
        fields = ['title', 'submission_status', ]
