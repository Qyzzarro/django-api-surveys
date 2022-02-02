from rest_framework.permissions import AllowAny, BasePermission, IsAdminUser


class AllowListAndRetrieve(BasePermission):
    def has_permission(self, request, view):
        return view.action in ["list", "retrieve"]


class DontShowUnpublished(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.is_published


class DontShowUnpublishedForNonStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.is_published or request.user.is_staff


class DontShowFakeAnswer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.type == "text"


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user == None:
            return True
        else:
            return obj.user == request.user or \
                request.user.is_superuser or \
                request.user.is_staff