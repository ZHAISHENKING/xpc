from django.http import HttpResponseRedirect

from web.helpers.utils import multi_encrypt
from web.models import Composer

need_login = ['/show_list/']


class AuthMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.path in need_login:
            cid = request.COOKIES.get('cid')
            auth = request.COOKIES.get('Authorization')
            composer = Composer.objects.filter(cid=cid).first()

            if composer and auth == multi_encrypt(composer.cid, composer.phone):
                request.composer = composer
            else:
                return HttpResponseRedirect('/login/')
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response