from hashlib import md5
from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.functional import cached_property
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from web.helpers.utils import multi_encrypt
from web.models import Post, Comment, Composer
from web.models import r


@cached_property
def count(self):
    """自定义一个count函数，替代Paginator内的count函数"""
    sql, params = self.object_list.query.sql_with_params()
    sql = sql % params
    cache_key = md5(sql.encode('utf-8')).hexdigest()
    # 先去redis内取
    rows = cache.get(cache_key)
    # 如果取不到，再去数据库内查询
    if not rows:
        rows = self.object_list.count()
        # 然后将查询结果存储到redis中， 这样下次就不必再查询数据库了
        # 设置1小时后过期，这样的话，1小时之后会再次查询数据库以得到最新的数量
        cache.set(cache_key, rows, timeout=60 * 60)
    return int(rows)
# 替换原有的count函数
Paginator.count = count


# @cache_page(60)
def show_list(request, page=1):
    cur_page = int(page)
    # 查询posts表，按play_counts倒序排序
    posts = Post.objects.order_by('-play_counts')
    paginator = Paginator(posts, 24)
    posts = paginator.page(cur_page)

    # 分页逻辑
    # 要显示的页码数量
    page_num = 5
    # 一半的页码数量
    half_page_num = page_num // 2
    first_page = 1
    last_page = paginator.num_pages
    # 如果处理当前页之前的页码不足2页
    if cur_page - half_page_num < 1:
        # 则显示的页码从当前页开始
        display_pages = range(cur_page, cur_page + page_num)
    # 如果处理当前页之后的页码不足2页
    elif cur_page + half_page_num > last_page:
        # 则从当前页往前数5页
        display_pages = range(cur_page - page_num, cur_page + 1)
    else:
        # 其他情况下，当前页左右各显示两页
        display_pages = range(cur_page - half_page_num, cur_page + half_page_num +1)
    display_pages = list(display_pages)
    # 是否显示下一页
    if posts.has_next():
        next_page = posts.next_page_number()
    # 是否显示上一页
    if posts.has_previous():
        previous_page = posts.previous_page_number()
    # 如果当前页码范围内不包含第一页，则把第一页添加进去
    if first_page not in display_pages:
        display_pages.insert(0, first_page)
    # 如果当前页码范围内不包含最后一页，则把最后页添加进去
    if last_page not in display_pages:
        display_pages.append(last_page)
    # 把所有的局部变量传给模板
    return render(request, 'post_list.html', locals())


def detail(request, pid):
    """视频详情页"""

    post = Post.get(pid=pid)
    return render(request, 'post.html', locals())


def comments(request):
    # id = 80498 & ajax = 1 & page = 1
    pid = request.GET.get('id')
    cur_page = request.GET.get('page', 1)
    comments = Comment.objects.filter(pid=pid)
    paginator = Paginator(comments, 10)
    comments = paginator.page(int(cur_page))
    for comment in comments:
        # reply字段存储的是commentid，如果reply不为0
        # 也就是说它是回复的另外一条评论
        comment.approved = ''
        cache_key = 'comment_likes_%s' % comment.commentid
        if r.sismember(cache_key, request.composer.cid):
            print('ismember', cache_key, request.composer.cid)
            comment.approved = 'approved'
        if comment.reply:
            # 把被回复的那评论加载出来，作为reply属性
            comment.reply = Comment.objects.filter(commentid=comment.reply).first()
            # comment.reply = Comment.objects.get(commentid=comment.reply)
    return render(request, 'comments.html', locals())


def like(request):
    # commentid: 46615  # 评论ID
    # type: 0
    # isLike: y/n  y表示点赞 n表示取消点赞
    like = request.POST.get('isLike', 'y')
    commentid = request.POST.get('commentid')
    comment = Comment.get(commentid=commentid)
    cache_key = 'comment_likes_%s' % commentid
    if r.sadd(cache_key, request.composer.cid):
        comment.like_counts += 1
        print('like=y')
        status = 1
    else:
        r.srem(cache_key, request.composer.cid)
        print('like=n')
        comment.like_counts -= 1
        status = 2

    print('comment.like_counts=%s' % comment.like_counts)
    comment.save()
    cache.set('Comment_%s' % comment.commentid, comment)

    return JsonResponse({
        "status": status,
        "user":{
            "userid":request.composer.cid
        }})
