from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings
from autoslug.fields import AutoSlugField
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    username = models.CharField(error_messages={'unique': 'A user with that username already exists.'},
                                help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                max_length=20, unique=True,
                                validators=[UnicodeUsernameValidator()],
                                verbose_name='username')
    email = models.EmailField(unique=True, db_index=True)
    slug = AutoSlugField(populate_from='username', unique=True, verbose_name='URL')
    bio = models.CharField(max_length=250, null=True)
    profile_photo = CloudinaryField('image', folder=f'avatars/', blank=True, null=True)

    def __str__(self):
        return self.username


class Following(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_followings')
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_followers')
    time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('follower', 'followed')


class News(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news')
    actions = [
        ('subscribe', 'subscribed to'),
        ('post', 'shared a '),
        ('avatar', 'changed avatar')
    ]
    action = models.CharField(max_length=255, choices=actions)
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

    class Meta:
        verbose_name_plural = 'News'


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_posts')
    created_date = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_post')
    tags = models.ManyToManyField('djangogramm.Tag', related_name='taged_posts')


class Image(models.Model):
    image = CloudinaryField('image', folder=f'post_media')
    post = models.ForeignKey('djangogramm.Post', related_name='images', on_delete=models.CASCADE)


class Tag(models.Model):
    name = models.CharField(max_length=30)
