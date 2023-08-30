from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_student


class IsCarer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_carer


class IsProgramAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_carer

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_carer and obj.author == request.user
