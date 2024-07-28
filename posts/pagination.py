from rest_framework.pagination import PageNumberPagination

class ItemPagination(PageNumberPagination):
    page_size = 25 
    page_size_query_param = 'page_size'  # /?page_size=xxx