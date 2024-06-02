from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math

class JobsPagination(PageNumberPagination):
    page_size = 100  # You can adjust the page size as per your requirement
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        total_count = self.page.paginator.count
        page_size = self.get_page_size(self.request)
        total_page_count = math.ceil(total_count / page_size)
        
        return Response({
            'status': True,
            'count': total_count,
            'total_page_count': total_page_count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class UsersPagination(PageNumberPagination):
    page_size = 100  # You can adjust the page size as per your requirement
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        total_count = self.page.paginator.count
        page_size = self.get_page_size(self.request)
        total_page_count = math.ceil(total_count / page_size)
        
        return Response({
            'status': True,
            'count': total_count,
            'total_page_count': total_page_count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })



class UsersJobsFeedbackPagination(PageNumberPagination):
    page_size = 5  # You can adjust the page size as per your requirement
    page_size_query_param = "page_size"
    max_page_size = 100

    # def get_paginated_response(self, data):
    #     total_count = self.page.paginator.count
    #     page_size = self.get_page_size(self.request)
    #     total_page_count = math.ceil(total_count / page_size)
        
    #     return Response({
    #         'status': True,
    #         'count': total_count,
    #         'total_page_count': total_page_count,
    #         'next': self.get_next_link(),
    #         'previous': self.get_previous_link(),
    #         'results': data
    #     })
