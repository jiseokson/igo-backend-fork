from rest_framework.permissions import BasePermission, SAFE_METHODS


class ProfileRetrievUpdatePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True
        return request.user == obj
