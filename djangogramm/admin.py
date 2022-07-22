from django.contrib import admin

from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'last_login',
        'is_superuser',
        'username',
        'is_staff',
        'is_active',
        'date_joined',
        'email',
        'slug',
        'bio',
        'profile_photo',
    )
    list_filter = (
        'last_login',
        'is_superuser',
        'is_staff',
        'is_active',
        'date_joined',
    )
    filter_horizontal = ('groups', 'user_permissions')
    search_fields = ('slug',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_date', 'text')
    list_filter = ('user', 'created_date')


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'post')
    list_filter = ('post',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'time', 'followed_user', 'post')
    list_filter = ('time',)

