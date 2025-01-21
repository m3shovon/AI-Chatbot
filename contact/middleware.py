# from datetime import datetime, timedelta
# from django.utils import timezone
# from django.shortcuts import redirect
# from django.urls import reverse
# from django.http import JsonResponse


# class SessionTimeoutMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if request.user.is_authenticated:
#             last_activity = request.session.get('last_activity')
#             now = timezone.now()

#             if last_activity:
#                 last_activity = datetime.fromisoformat(last_activity)

#                 if (now - last_activity) > timedelta(minutes=1):
#                     del request.session['last_activity']
#                     request.session.flush()
#                     return JsonResponse({'session_timeout': True})

#             request.session['last_activity'] = now.isoformat()

#         response = self.get_response(request)
#         return response
