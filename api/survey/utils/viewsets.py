from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


class PermissedModelViewset(ModelViewSet):
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        candidates = [query for query in queryset]
        unwanteds = []
        for obj in candidates:
            for permission in self.get_permissions():
                if not permission.has_object_permission(request, self, obj):
                    unwanteds.append(obj)
        for unwanted in unwanteds:
            candidates.remove(unwanted)

        page = self.paginate_queryset(candidates)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
