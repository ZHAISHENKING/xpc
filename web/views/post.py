from django.shortcuts import render
from django.core.paginator import Paginator
from web.models import Post


def show_list(request):
    posts = Post.objects.order_by('-play_counts')
    paginator = Paginator(posts, 24)
    posts = paginator.page(1)
    return render(request, 'post_list.html', {'posts': posts})