from rest_framework import permissions


class IsMeOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, user):
        return (request.method in permissions.SAFE_METHODS) or (user == request.user)


class IsMe(permissions.BasePermission):

    def has_permission(self, request, view):
        return (view.kwargs['pk'].isdigit() and request.user.id == int(view.kwargs['pk'])) or view.kwargs['pk'] == 'me'
