# decorators.py
# decorators.py

from functools import wraps
from django.http import JsonResponse

def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        print(f"User authenticated: {request.user.is_authenticated}")
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return JsonResponse({'status': 'Unauthorized', 'message': 'Authentication required'}, status=401)
    return _wrapped_view
