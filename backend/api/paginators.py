from rest_framework.pagination import PageNumberPagination

from api.constants import PAGE_SIZE


class PageNumberLimitPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    max_page_size = 100
    page_size_query_param = 'limit'
