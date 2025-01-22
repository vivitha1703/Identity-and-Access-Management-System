from django.http import HttpResponse
from functools import wraps

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.role == required_role:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponse("Unauthorized access: Insufficient permissions", status=403)
            return redirect('login-view')
        return _wrapped_view
    return decorator
