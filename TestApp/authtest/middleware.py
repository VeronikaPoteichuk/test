from django.http import HttpResponseForbidden
from django.urls import resolve

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if resolve(request.path).app_name == 'admin':
            if not request.user.is_authenticated or not request.user.is_staff:
                return HttpResponseForbidden("Forbidden")
        return self.get_response(request)
