from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from storages.backends.s3boto3 import S3Boto3Storage
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from autoslug.fields import AutoSlugField
from datetime import date
import string
from random import choices


def rename_avatar(instance, filename):
    extension = filename.split(".")[-1]
    rename = instance.username
    return f'avatars/{rename}.{extension}'


def rename_media(instance, filename):
    today = date.today()
    rename = f'{instance.post.user.username}_{instance.post.pk}_{filename}'
    return f'media/{today.strftime("%Y/%m/%d")}/{rename}'


class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)
    slug = AutoSlugField(populate_from='username', unique=True, verbose_name='URL')
    bio = models.CharField(max_length=250, null=True)
    profile_photo = ThumbnailerImageField(upload_to=rename_avatar,
                                          blank=True,
                                          thumbnail_storage=S3Boto3Storage,
                                          resize_source=dict(size=(250, 250)))

    def __str__(self):
        return self.username


class Following(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='follower')
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed')
    time = models.DateTimeField(auto_now=True)


class News(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news')
    action = models.CharField(max_length=255)
    time = models.DateTimeField(auto_now=True)
    followed_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      on_delete=models.CASCADE,
                                      default=None,
                                      blank=True,
                                      null=True,
                                      related_name='news_followed_user')
    post = models.ForeignKey('Post',
                             on_delete=models.CASCADE,
                             default=None,
                             blank=True,
                             null=True)


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_posts')
    created_date = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_post')
    tags = models.ManyToManyField('djangogramm.Tag', related_name='taged_posts')


class Image(models.Model):
    image = ThumbnailerImageField(upload_to=rename_media,
                                  blank=True,
                                  thumbnail_storage=S3Boto3Storage,
                                  resize_source=dict(size=(250, 250))
                                  )
    post = models.ForeignKey('djangogramm.Post', related_name='images', on_delete=models.CASCADE)


class Tag(models.Model):
    name = models.CharField(max_length=30)
