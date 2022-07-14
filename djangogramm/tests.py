from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from .models import *
from django.contrib.auth import get_user_model
from easy_thumbnails.files import ThumbnailerImageFieldFile
import shutil
import tempfile


class Settings(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create authorized user
        user = get_user_model()
        cls.user = user.objects.create_user(username='Test_user')
        cls.client = Client()
        cls.client.force_login(cls.user)
        # create post
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        post = Post.objects.create(user_id=cls.user.pk, text='Test post')
        image = Image.objects.create(
            image=tempfile.NamedTemporaryFile(suffix='.jpg').name,
            post=post)
        cls.test_image = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00' \
                         b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)


class LikeTest(Settings):
    def test_like(self):
        # like
        response_like = self.client.post(reverse('post_like'), data={'post_id': 1, 'user_id': 1})
        self.assertIs(response_like.status_code, 200)
        self.assertIs(Post.objects.get(id=1).likes.count(), 1)
        # unlike
        response_unlike = self.client.post(reverse('post_like'), data={'post_id': 1, 'user_id': 1})
        self.assertIs(response_unlike.status_code, 200)
        self.assertIs(Post.objects.get(id=1).likes.count(), 0)


class SetActiveTest(Settings):
    def test_set_active(self):
        user = User.objects.get(id=1)
        user.is_active = False
        user.save()
        # set active
        response1 = self.client.get(reverse('set_active', args=[user.username, user.validation_key]))
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        # click the link second time
        response2 = self.client.get(reverse('set_active', args=[user.username, user.validation_key]))
        self.assertEqual(response2.status_code, 404)


class EditUserTest(Settings):
    def test_edit_user(self):
        self.client.force_login(self.user)
        image = tempfile.mkstemp(suffix='.jpg')[1]
        photo = SimpleUploadedFile(image, content=self.test_image, content_type='image/jpeg')
        response = self.client.post(reverse('user_edit'),
                                    data={'bio': 'PRIVET', 'profile_photo': photo},
                                    format='multipart')
        user = User.objects.get(id=1)
        self.assertEqual(user.bio, 'PRIVET')
        self.assertEqual(response["Location"], reverse('user', args=[user.slug]))
        self.assertIsInstance(user.profile_photo, ThumbnailerImageFieldFile)


class CreatePostTest(Settings):
    def test_create_post(self):
        self.client.force_login(self.user)
        images = [tempfile.mkstemp(suffix='.jpg')[1] for i in range(5)]
        image_objects = [SimpleUploadedFile(image,
                                            content=self.test_image,
                                            content_type='image/jpeg') for image in images]
        response = self.client.post(reverse('create_post'),
                                    data={'text': 'Hi', 'images': image_objects},
                                    format='multipart')
        post = Post.objects.last()
        self.assertEqual(response['Location'], reverse('user', args=[self.user.slug]))
        self.assertEqual(post.text, 'Hi')
        self.assertEqual(post.images.count(), 5)

    def test_create_post_with_tag(self):
        self.client.force_login(self.user)
        image = SimpleUploadedFile(tempfile.mkstemp(suffix='.jpg')[1],
                                   content=self.test_image,
                                   content_type='image/jpeg')
        text = 'This is test post #new #post #python #hello. #123hello123 #tag_with_underline'
        response = self.client.post(reverse('create_post'),
                                    data={'text': text, 'images': image},
                                    format='multipart')
        for tag in ('#new', '#post', '#python', '#hello', '#123hello123', '#tag_with_underline'):
            tag_from_base = Tag.objects.filter(name=tag).first()
            self.assertIsInstance(tag_from_base, Tag)