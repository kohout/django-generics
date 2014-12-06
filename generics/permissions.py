# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.decorators import method_decorator
from django.conf import settings

def get_login_url():
    login_view = getattr(settings, 'LOGIN_URL', None)
    if not login_view:
        return '/'
    return reverse_lazy(login_view)

""" Methods """


def is_user_verified(user):
    return user.is_user_verified()


def superuser_required(function=None,
                       redirect_field_name=REDIRECT_FIELD_NAME,
                       login_url=None):
    """
    Decorator for views that checks that the user is logged in and its
    superuser-status is set
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_superuser,
        login_url=get_login_url(),
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def staff_required(function=None,
                       redirect_field_name=REDIRECT_FIELD_NAME,
                       login_url=None):
    """
    Decorator for views that checks that the user is logged in and its
    superuser-status is set
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_staff,
        login_url=get_login_url(),
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def staff_or_superuser_required(function=None,
                       redirect_field_name=REDIRECT_FIELD_NAME,
                       login_url=None):
    """
    Decorator for views that checks that the user is logged in and its
    superuser-status is set
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and (u.is_staff or u.is_superuser),
        login_url=get_login_url(),
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


""" Mixins for Views """


class LoginRequiredMixin(object):
    """
    Any authenticated user (committed or not committed)
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class StaffRequired(object):
    """
    Any authenticated user (committed or not committed)
    """
    @method_decorator(staff_required)
    def dispatch(self, *args, **kwargs):
        return super(StaffRequired,
            self).dispatch(*args, **kwargs)

class SuperUserRequired(object):
    """
    only superuser
    """
    @method_decorator(superuser_required)
    def dispatch(self, *args, **kwargs):
        return super(SuperUserRequired,
            self).dispatch(*args, **kwargs)

class StaffOrSuperUserRequired(object):
    """
    staff and superuser are allowed to access this view
    """
    @method_decorator(staff_or_superuser_required)
    def dispatch(self, *args, **kwargs):
        return super(StaffOrSuperUserRequired,
            self).dispatch(*args, **kwargs)
