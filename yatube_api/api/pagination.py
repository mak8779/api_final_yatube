from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomPagination(LimitOffsetPagination):

    def get_paginated_response(self, data):
        if (
            'limit' in self.request.query_params
            or 'offset' in self.request.query_params
        ):
            return Response({
                'count': self.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            })

        return Response(data)
