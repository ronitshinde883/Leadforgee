from rest_framework.permissions import BasePermission

class IsCompanyAdmin(BasePermission):
    """
        Allows only access to company admins
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False
        
        return user.userprofile.role == "admin"

class IsTaskOwner(BasePermission):
    """
        Allows only the task owner to perform actions
    """

    def has_object_permission(self, request, view, obj):
        return obj.assigned_to == request.user
