from django.http import HttpResponseRedirect

from web.helpers.utils import multi_encrypt
from web.models import Composer

not_need_login = ['/login/', '/register/', '/find_password/', '/api/v1/user/login']
need_login = ['/logout/',
              '/article/comment/ts-ajax_do',
              '/article/filmplay/ts-approve',
              ]


class AuthMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        cid = request.COOKIES.get('cid')
        auth = request.COOKIES.get('Authorization')
        composer = Composer.objects.filter(cid=cid).first()

        if composer and auth == multi_encrypt(composer.cid, composer.phone):
            request.composer = composer
        else:
            composer = Composer()
            composer.cid = 0
            request.composer = composer
            if request.path in need_login:
                return HttpResponseRedirect('/login/')
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response