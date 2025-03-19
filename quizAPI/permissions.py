from rest_framework import permissions

# permissions to view/access the API
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user
# permissions to view user lists
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user

# permissions to view/edit collections
class IsOwnerOrSharedReadOnly(permissions.BasePermission):

    """
    Custom permission: 
    - Owners can edit/delete.
    - Users in `shared_with` can only read.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user == obj.owner or request.user in obj.shared_with.all()
        return request.user == obj.owner