from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class LargePagination(PageNumberPagination):
    page_size = 1000 # Untuk dropdown jika datanya banyak sekali
    max_page_size = 5000