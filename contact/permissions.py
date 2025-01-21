from rest_framework import permissions
from rest_framework.permissions import (DjangoModelPermissions)


class UpdateOwnProfile(permissions.BasePermission):
    """Allow user to edit their own profile"""
    
    def has_object_permission(self, request, view, obj):
        """Check user is trying to edit their own profile"""
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.id == request.user.id or request.user.is_superuser
    
    
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or request.user.is_superuser


class Profilepermission(permissions.BasePermission):
    """Allow user to edit contact"""
    
    def has_object_permission(self, request, view, obj):
        """Check user is trying to edit their own profile"""
        if request.method in permissions.SAFE_METHODS:
            return True

class CustomDjangoModelPermissions(DjangoModelPermissions):
    def __init__(self):
        # self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        pass
       