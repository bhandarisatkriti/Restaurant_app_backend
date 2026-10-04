from rest_framework import permissions

class IsOwnerorReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'owner'
class IsStaffOrOwner(permissions.BasePermission):
    """
    Only staff or owner can access. Customers are blocked entirely.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ['staff', 'owner']
        )