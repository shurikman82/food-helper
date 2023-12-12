from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 'limit'
    page_size_query_param = 'limit'
