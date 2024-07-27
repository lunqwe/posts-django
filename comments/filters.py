from django_filters import FilterSet, DateFilter
from .models import Comment

class CommentFilter(FilterSet):
    date_from = DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = DateFilter(field_name='created_at', lookup_expr='lte')
    class Meta:
        model = Comment
        fields = ['text', 'owner', 'post', 'date_from', 'date_to']
        
