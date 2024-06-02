from rest_framework.pagination import PageNumberPagination


class JobsPagination(PageNumberPagination):
    page_size = 10  # You can adjust the page size as per your requirement
    page_size_query_param = "page_size"
    max_page_size = 100
