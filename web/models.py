# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals
import random
import pickle
import redis
from django.db import models
from django.core.cache import cache

r = redis.Redis(host='zskin.xin')


class Model(object):
    @classmethod
    def get(cls, **kwargs):
        """按主键查询，并设置到缓存中，下次就直接可以从缓存中获取指定的数据"""
        cache_key = '%s_%s' % (cls.__name__, next(iter(kwargs.values())))
        obj = cache.get(cache_key)
        if not obj:
            obj = cls.objects.get(**kwargs)
            cache.set(cache_key, obj)
        return obj


class Comment(models.Model, Model):
    commentid = models.IntegerField(primary_key=True)
    pid = models.BigIntegerField()
    cid = models.BigIntegerField()
    avatar = models.CharField(max_length=512, blank=True, null=True)
    uname = models.CharField(max_length=512, blank=True, null=True)
    created_at = models.CharField(max_length=128)
    content = models.TextField(blank=True, null=True)
    like_counts = models.IntegerField()
    reply = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'comments'


class Composer(models.Model, Model):
    cid = models.BigIntegerField(primary_key=True)
    banner = models.CharField(max_length=512)
    avatar = models.CharField(max_length=512)
    verified = models.CharField(max_length=128, blank=True, null=True)
    name = models.CharField(max_length=128)
    intro = models.TextField(blank=True, null=True)
    like_counts = models.IntegerField(default=0)
    fans_counts = models.IntegerField(default=0)
    follow_counts = models.IntegerField(default=0)
    location = models.CharField(max_length=512)
    career = models.CharField(max_length=512)
    phone = models.CharField(max_length=11, blank=True, null=True)
    password = models.CharField(max_length=36, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'composers'

    @property
    def posts(self):
        cache_key = 'cr_list_cid_%s' % self.cid
        posts = [pickle.loads(post) for post in r.lrange(cache_key, 0, -1)]
        if not posts:
            cr_list = Copyright.objects.filter(cid=self.cid).all()
            for cr in cr_list:
                post = Post.get(pid=cr.pid)
                post.roles = cr.roles
                posts.append(post)
                # r.rpush(cache_key, pickle.dumps(post))
            r.rpush(cache_key, *[pickle.dumps(post) for post in posts])
        return posts


class Copyright(models.Model, Model):
    pcid = models.CharField(primary_key=True, max_length=32)
    pid = models.BigIntegerField()
    cid = models.BigIntegerField()
    roles = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'copyrights'


class Post(models.Model, Model):
    pid = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=256)
    thumbnail = models.CharField(max_length=512, blank=True, null=True)
    preview = models.CharField(max_length=512, blank=True, null=True)
    video = models.CharField(max_length=512, blank=True, null=True)
    video_format = models.CharField(max_length=32, blank=True, null=True)
    category = models.CharField(max_length=512)
    duration = models.IntegerField()
    created_at = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    play_counts = models.IntegerField()
    like_counts = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'posts'

    def durations(self):
        # 取两个数的商和余数
        minutes, seconds = divmod(self.duration, 60)
        # 指定字符串的宽度为2，如果不足2位，在前面添加0
        minutes = str(minutes).zfill(2)
        seconds = str(seconds).zfill(2)
        return "%s' %s''" % (minutes, seconds)

    @property
    def composers(self):
        """获取当前作品的所有作者信息"""

        cache_key = 'cr_list_pid_%s' % self.pid
        composers = [pickle.loads(composer) for composer in r.lrange(cache_key, 0, -1)]
        if not composers:
            # 先查询copyright中间表，得到作品和作者的对应关系
            cr_list = Copyright.objects.filter(pid=self.pid).all()
            for cr in cr_list:
                # 获取Composer对象
                composer = Composer.get(cid=cr.cid)
                composer.roles = cr.roles
                # 放到一个列表
                composers.append(composer)
            r.lpush(cache_key, *[pickle.dumps(composer) for composer in composers])

        # 返回composer对象列表
        return composers

    @property
    def background(self):
        if not self.preview:
            return ''
        raw_img, sep, param = self.preview.partition('@')
        param = "960w_540h_50-30bl_1e_1c"
        return '%s%s%s' % (raw_img, sep, param)


class Code(models.Model, Model):
    code_id = models.BigAutoField(primary_key=True)
    phone = models.BigIntegerField()
    code = models.BigIntegerField()
    created_at = models.DateTimeField()
    ip = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'codes'

    def gen_code(self):
        self.code = str(random.randint(100000, 999999))
        return self.code