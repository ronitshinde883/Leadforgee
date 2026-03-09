from rest_framework.authentication import SessionAuthentication

"""
    DISABLED CSRF TEMPORARILY
"""

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return