from django.shortcuts import redirect

class SuspensionMiddleware:
    """
    Middleware for redirecting suspended users to the suspended page.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.redirected = False

    def __call__(self, request):
        """
        Boilerplate for Django middleware machinery.
        """
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Redirect the user to the suspended page if she is suspended.
        """
        user = request.user

        if user.is_anonymous():
            return None

        if user.is_superuser:
            return None

        uri = request.build_absolute_uri()

        if uri[-8:] == "/logout/":
            return None

        if uri[-20:] == "/accounts/suspended/" and not self.redirected:
            return None

        if user.suspensioninfo.suspended:
            if self.redirected:
                self.redirected = False
                return None
            else:
                self.redirected = True
                return redirect("suspended")
        else:
            return None
