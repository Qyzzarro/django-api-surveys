from rest_framework.viewsets import (mixins, GenericViewSet,)
from rest_framework.request import Request
from rest_framework.response import Response


class PermissedRetrieveModelMixin(mixins.RetrieveModelMixin):
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PermissedListModelMixin(mixins.ListModelMixin):
    def __filter_via_object_permitions(self, request: Request, objs: list) -> list:
        unwanteds = []
        for obj in objs:
            for permission in self.get_permissions():
                if not permission.has_object_permission(request, self, obj):
                    unwanteds.append(obj)
        for unwanted in unwanteds:
            objs.remove(unwanted)

        return objs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        candidates = [query for query in queryset]
        filtereds = self.__filter_via_object_permitions(request, candidates)
        page = self.paginate_queryset(filtereds)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)


class PermissedModelViewset(mixins.CreateModelMixin,
                            PermissedRetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            PermissedListModelMixin,
                            GenericViewSet):
    pass
