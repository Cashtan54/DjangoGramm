from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.conf import settings
from unittest.mock import patch
from django.urls import reverse
from .models import *
from django.contrib.auth import get_user_model
from easy_thumbnails.files import ThumbnailerImageFieldFile
from django.core.signing import Signer
from io import BytesIO
from PIL import Image as PIL_Image
from django.core.files.base import ContentFile
import shutil
import tempfile
import cloudinary
from cloudinary import CloudinaryResource


def test_cloudinary(file, **kwargs):
    return {'public_id': None, 'version': '1.29.0',
            'format': None, 'type': None, 'resource_type': None}


class Settings(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create authorized user
        user = get_user_model()
        cls.user = user.objects.create_user(username='Test_user', email='123@gmail.com')
        cls.client = Client()
        cls.client.force_login(cls.user)
        # create post
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        post = Post.objects.create(user_id=cls.user.pk, text='Test post')
        post_image = Image.objects.create(image=tempfile.NamedTemporaryFile(suffix='.jpg').name,
                                          post=post)
        cls.bytes_img = BytesIO(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00'
                                b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)


class LikeTest(Settings):
    def test_like(self):
        self.client.force_login(self.user)
        # like
        response_like = self.client.post(reverse('post_like'), data={'post_id': 1})
        self.assertIs(response_like.status_code, 200)
        self.assertIs(Post.objects.get(id=1).likes.count(), 1)
        # unlike
        response_unlike = self.client.post(reverse('post_like'), data={'post_id': 1})
        self.assertIs(response_unlike.status_code, 200)
        self.assertIs(Post.objects.get(id=1).likes.count(), 0)


class SetActiveTest(Settings):
    def test_set_active(self):
        self.user.is_active = False
        self.user.save()
        signer = Signer(salt='django')
        response1 = self.client.get(reverse('set_active',
                                            args=[self.user.username, signer.sign(self.user.email)]))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


class EditUserTest(Settings):
    @patch('cloudinary.uploader.upload', new=test_cloudinary)
    def test_edit_user(self):
        self.client.force_login(self.user)
        test_image = self.bytes_img
        test_image.name = 'myimage.jpg'
        response = self.client.post(reverse('user_edit'),
                                    data={'bio': 'PRIVET', 'profile_photo': test_image},
                                    format='multipart')
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, 'PRIVET')
        self.assertEqual(response["Location"], reverse('user', args=[self.user.slug]))
        self.assertIsInstance(self.user.profile_photo, CloudinaryResource)


class CreatePostTest(Settings):
    @patch('cloudinary.uploader.upload', new=test_cloudinary)
    def test_create_post(self):
        self.client.force_login(self.user)
        text = 'This is test post #new #post #python #hello. #123hello123 #tag_with_underline'
        test_image = self.bytes_img
        test_image.name = 'myimage.jpg'
        response = self.client.post(reverse('create_post'),
                                    data={'text': text, 'images': test_image},
                                    format='multipart')
        post = Post.objects.last()
        self.assertEqual(post.text, text)
        self.assertEqual(response['Location'], reverse('user', args=[self.user.slug]))
        self.assertEqual(post.images.count(), 1)
        for tag in ('#new', '#post', '#python', '#hello', '#123hello123', '#tag_with_underline'):
            tag_from_base = Tag.objects.filter(name=tag).first()
            self.assertIsInstance(tag_from_base, Tag)


class FollowTest(Settings):
    def test_follow(self):
        self.client.force_login(self.user)
        User.objects.create(username='Test_user2')
        user_to_follow_id = User.objects.get(username='Test_user2').id
        # follow
        response_follow = self.client.post(reverse('follow'), data={'user_to_follow': user_to_follow_id})
        self.assertIs(response_follow.status_code, 200)
        self.assertIs(Following.objects.filter(follower=self.user).count(), 1)
        # unfollow
        response_unfollow = self.client.post(reverse('follow'), data={'user_to_follow': user_to_follow_id})
        self.assertIs(response_unfollow.status_code, 200)
        self.assertIs(Following.objects.filter(follower=self.user).count(), 0)
