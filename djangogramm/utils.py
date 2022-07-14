from django.contrib.auth.backends import ModelBackend, UserModel
from django.db.models import Q
from re import findall
from .models import Post, Image, Tag
from django.core.mail import send_mail
from django.conf import settings


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def get_user(self, user_id):
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None


def save_image_to_post(post, images):
    for image_file in images:
        if image_file:
            Image.objects.create(image=image_file, post=post)


def save_tags_to_post(post, text):
    tags = [tag.lower() for tag in findall(r'#[\w\d_]+', text)]
    for tag in tags:
        tag_in_base = Tag.objects.get_or_create(name=tag)[0]
        post.tags.add(tag_in_base)


def send_email(email, username, validate_key):
    # send email using the self.cleaned_data dictionary
    subject = 'Welcome to DjangoGramm'
    link = f'http://djangogramm-romantsov.herokuapp.com/sign_up/{username}/{validate_key}'
    message = f'Click the link to validate email adress\n{link}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email, ])
