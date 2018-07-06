"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView
from web.views import post, composer


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^show_list/$', post.show_list),
    url(r'^show_list/(?P<page>\d+)/$', post.show_list),
    url(r'^user/oneuser/userid-(?P<cid>\d+)$', composer.oneuser),
    url(r'^u(?P<cid>\d+)$', composer.homepage),
    url(r'^a(?P<pid>\d+)$', post.detail),
    url(r'^article/filmplay/ts-getCommentApi$', post.comments),
    url(r'^register$', TemplateView.as_view(template_name='register.html')),  # 显示注册页面
    url(r'^api/v1/mobile/send$', composer.send_code),  # 发送手机验证码
    url(r'^api/v1/user/register$', composer.do_register),  # 执行注册操作
    url(r'^login/$', TemplateView.as_view(template_name='login.html')),  # 显示登录页面
    url(r'^api/v1/user/login$', composer.do_login),  # 执行登录操作
    url(r'^logout/$', composer.logout),  # 执行注销操作
    # 忘记密码页面
    url(r'^find_password/$',
        TemplateView.as_view(template_name='find_password.html')),
    url(r'^api/v1/user/check/send$', composer.check_send),
    url(r'^api/v1/mobile/check/find$', composer.mobile_check),
    url(r'^api/v1/user/findPwd$', composer.find_password),
]
