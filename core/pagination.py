from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response

class StandardResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"  # El cliente puede pedir: ?page_size=50
    max_page_size = 100


class StudentCursorPagination(CursorPagination):
    """Cursor pagination para estudiantes con respuesta compatible con tests."""

    page_size = 20
    ordering = "-created_at"
    cursor_query_param = "cursor"

    def paginate_queryset(self, queryset, request, view=None):
        self.count = queryset.count()
        return super().paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
