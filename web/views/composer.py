from hashlib import md5
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from web.models import Post, Composer, Code
from web.helpers.utils import multi_encrypt, send_sms_code


def oneuser(request, cid):
    composer = Composer.get(cid=cid)
    composer.recent_posts = composer.posts[:2]
    return render(request, 'oneuser.html', locals())


def homepage(request, cid):
    composer = Composer.get(cid=cid)
    first_post, *rest_posts = composer.posts
    return render(request, 'homepage.html', locals())


def send_code(request):
    """注册发送手机验证码"""
    # 接受的参数
    # is_register: 1
    # phone: 13601058935
    # prefix_code: +86
    phone = request.POST.get('phone')
    # 先验证该手机有没有注册过
    composer = Composer.objects.filter(phone=phone).first()
    if composer:
        return JsonResponse({"status":-1025,"msg":"该手机号已注册过"})
    # 发送短信验证码
    code = Code()
    code.phone = phone
    code.created_at = datetime.now()
    code.ip = request.META.get('REMOTE_ADDR')
    code.gen_code()
    code.save()
    send_sms_code(phone, code.code)
    # 返回json
    return JsonResponse({
            "status": 0,
            "msg": "OK",
            "data": {
                 "phone": phone,
                 "prefix_code": "+86"}})


def do_register(request):
    # nickname: sssss
    # phone: 13136130957
    # code: 432424
    # password: 432443
    # prefix_code: +86
    nickname = request.POST.get('nickname')
    phone = request.POST.get('phone')
    code = request.POST.get('code')
    password = request.POST.get('password')
    # 先查找一下验证码，看看验证是否正确
    co = Code.objects.filter(phone=phone, code=code).first()
    if not co:
        return JsonResponse({"status":-1,"msg":"手机验证失败"})
    # 如果验证码超过10分钟，则也视为失败
    delay = (datetime.now() - co.created_at.replace(tzinfo=None)).total_seconds()
    if delay > 60 * 10:
        return JsonResponse({"status":-1,"msg":"手机验证失败"})
    # 创建用户对象
    composer = Composer()
    composer.cid = composer.phone = phone
    composer.name = nickname
    # 注意：：：将用户密码加密后再存入到数据库
    composer.password = multi_encrypt(password, phone)
    composer.save()
    return JsonResponse({
        "status": 0,
        "msg": "手机验证成功",
        "data": {
            "callback": "/show_list/",
        }
    })


def do_login(request):
    # prefix_code: +86
    # type: phone
    # value: 13136130957
    # password: sfsdfsa

    phone = request.POST.get('value')
    password = request.POST.get('password')
    composer = Composer.objects.filter(phone=phone).first()
    if not composer:
        return JsonResponse({"status":-1,"msg":"用户名或密码错误"})
    # 验证密码的时候和注册一样，先将密码加密后再与数据库中的密码字符串比对
    if composer.password != multi_encrypt(password, phone):
        return JsonResponse({"status":-1,"msg":"用户名或密码错误"})

    response = JsonResponse({
        "status": 0,
        "msg": "登录成功",
        "data": {
            "callback": "/show_list/",
        }
    })
    # 将登录成功的凭证（也就是Authorization）写入cookie
    response.set_cookie('cid', composer.cid)
    response.set_cookie('Authorization',
                multi_encrypt(composer.cid, composer.phone))
    return response


def logout(request):
    """注销登录"""
    response = HttpResponseRedirect('/login/')
    response.delete_cookie('cid')
    # 将登录成功的凭证（也就是Authorization）从cookie中删除
    response.delete_cookie('Authorization')
    return response


def check_send(request):
    """找回密码1 发送验证码"""
    phone = request.POST.get('phone')
    # 先看看用户是否存在
    composer = Composer.objects.filter(phone=phone).first()
    if not composer:
        # 如果不存在也不能明确告知客户端不存在
        return JsonResponse({"status": 0, "msg": "OK"})
    # 发送验证码先验证手机号是否属于用户本人
    code = Code()
    code.phone = phone
    code.created_at = datetime.now()
    code.ip = request.META.get('REMOTE_ADDR')
    code.gen_code()
    code.save()
    send_sms_code(phone, code.code)
    return JsonResponse({
        "status": 0,
        "msg": "OK",
        "data": {
            "phone": phone,
            "prefix_code": "+86"}})


def mobile_check(request):
    """找回密码2 验证手机号和验码码"""
    phone = request.POST.get('phone')
    code = request.POST.get('code')
    # 先查看用户是否存在
    composer = Composer.objects.filter(phone=phone).first()
    if not composer:
        return JsonResponse({"status": 0, "msg": "OK"})
    # 再验证手机号和验证码是否正确
    co = Code.objects.filter(phone=phone, code=code).first()
    if not co:
        return JsonResponse({"status":-1010,"msg":"校验手机验证码失败"})
    delay = (datetime.now() - co.created_at.replace(tzinfo=None)).total_seconds()
    # 如果验证码超过10分钟，则也视为失败
    if delay > 60 * 10:
        return JsonResponse({"status":-1010,"msg":"校验手机验证码失败"})
    response = JsonResponse({"status": 0, "msg": "OK"})
    # 颁发一个临时的验证cookies（find_pwd_sessionid），以识别他的身份
    response.set_cookie('phone', phone)
    response.set_cookie('find_pwd_sessionid', multi_encrypt(composer.cid, composer.phone))
    return response


def find_password(request):
    """找回密码3 重置密码"""
    # password: 123456
    # reset_password: 123456
    password = request.POST.get('password')
    confirm_pwd = request.POST.get('reset_password')
    if password != confirm_pwd:
        return JsonResponse({'status': -1, 'msg': '密码不一致'})
    phone = request.COOKIES.get('phone')
    sessionid = request.COOKIES.get('find_pwd_sessionid')
    composer = Composer.objects.filter(phone=phone).first()
    if not composer:
        return JsonResponse({"status": 0, "msg": "OK"})
    # 判断用户是否已经验证过手机号和验证码
    if sessionid != multi_encrypt(composer.cid, composer.phone):
        return JsonResponse({'status': -1, 'msg': 'session验证失败'})
    # 如果验证通过，则重置密码，注意密码需要加密后再存储
    composer.password = multi_encrypt(password, phone)
    composer.save()
    response = JsonResponse({
        "status": 0,
        "msg": "找回密码成功",
        "data": {
            "callback": "/login/",
        }
    })
    # 清除在第2步临时颁发的cookies
    response.delete_cookie('phone')
    response.delete_cookie('find_pwd_sessionid')
    return response

