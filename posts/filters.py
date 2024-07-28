from django_filters import FilterSet, DateFilter
from .models import Post

class PostFilter(FilterSet):
    date_from = DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = DateFilter(field_name='created_at', lookup_expr='lte')
    class Meta:
        model = Post
        fields = {'text': ['icontains', 'exact'],
                  'owner': ['exact'],
                  }
        extra_fields = ['date_from', 'date_to']