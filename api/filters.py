""" Module for filtering Project data """
import django_filters
from api.models import Project

class ProjectFilter(django_filters.FilterSet):
    """ Class for Project filtering """
    area_filter = django_filters.CharFilter(
        field_name='dimension_display_value', lookup_expr='startswith'
    )
    data_area_id = django_filters.CharFilter(
        field_name='data_area_id', lookup_expr='exact'
    )

    class Meta:
        model = Project
        fields = ['area_filter', 'data_area_id']
