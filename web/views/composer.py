from django.shortcuts import render
from django.core.paginator import Paginator
from web.models import Post, Composer


def oneuser(request, cid):
    composer = Composer.objects.get(cid=cid)
    composer.recent_posts = composer.posts[:2]
    return render(request, 'oneuser.html', locals())


def homepage(request, cid):
    composer = Composer.objects.get(cid=cid)
    first_post, *rest_posts = composer.posts
    return render(request, 'homepage.html', locals())
