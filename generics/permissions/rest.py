# -*- coding: utf-8 -*-
try:
    from rest_framework import permissions

    class IsOwnerOrIsStaffOrIsReadOnly(permissions.BasePermission):
        """
        Object-level permission to only allow owners of an object to edit it.
        Assumes the model instance has an `owner` attribute.
        """

        def has_object_permission(self, request, view, obj):
            # Read permissions are allowed to any request,
            # so we'll always allow GET, HEAD or OPTIONS requests.
            if request.method in permissions.SAFE_METHODS:
                return True

            # Instance must have an attribute named `owner`.
            if obj.owner == request.user:
                return True

            # Is Admin or Staff
            return request.user.is_staff or request.user.is_superuser
except ImportError:
    pass


try:
    from rest_framework import permissions
    from allauth.account.models import EmailAddress
    from core.auth.models import User

    class IsVerifiedOrIsStaffOrIsReadOnly(permissions.BasePermission):
        """
        Checks whether the user has verified the email adress given
        """

        def has_permission(self, request, view):
            if request.method in permissions.SAFE_METHODS:
                return True

            if isinstance(request.user, User):
                if request.user.is_staff or request.user.is_superuser:
                    return True

                return EmailAddress.objects.filter(user=request.user,
                                                   verified=True).exists()

            return False
except ImportError:
    pass
