from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse, Http404
from .models import *
from django.views.generic import CreateView, ListView, DetailView, FormView
from .forms import *
from .utils import save_image_to_post, save_tags_to_post, send_email
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


class SignUpView(CreateView):
    form_class = MyUserCreationForm
    template_name = 'djangogramm/sign_up.html'

    def form_valid(self, form):
        form.instance.is_active = False
        return super().form_valid(form)

    def get_success_url(self):
        user = self.object
        send_email(user.email, user.username, user.validation_key)
        return reverse_lazy('validate')


class Login(LoginView):
    template_name = 'djangogramm/login.html'
    success_url = reverse_lazy('feed')


class Logout(LogoutView):
    pass


class PostsView(ListView):
    model = Post
    template_name = 'djangogramm/feed.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.order_by('-created_date')[:20].select_related('user').prefetch_related('likes', 'images')


class UserView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'djangogramm/user.html'
    slug_url_kwarg = 'user_slug'
    context_object_name = 'profile'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = (Post.objects.filter(user=self.object).
                            order_by('-created_date').
                            select_related('user').
                            prefetch_related('likes', 'images')
                            )
        return context


class UserEdit(LoginRequiredMixin, FormView):
    form_class = MyUserChangeForm
    template_name = 'djangogramm/user_edit.html'

    def get_success_url(self):
        return reverse_lazy('user', kwargs={'user_slug': self.request.user.slug})

    def form_valid(self, form):
        user = User.objects.get(username=self.request.user.username)
        profile_photo = self.request.FILES.get('profile_photo', None)
        if profile_photo:
            user.profile_photo = profile_photo
        else:
            user.profile_photo.delete()
        user.bio = form.cleaned_data['bio']
        user.save()
        return super().form_valid(form)

    def get_initial(self):
        current_photo = self.request.user.profile_photo
        if current_photo:
            return {'bio': self.request.user.bio, 'profile_photo': current_photo}
        else:
            return {'bio': self.request.user.bio}


class CreatePost(LoginRequiredMixin, FormView):
    form_class = CreatePostForm
    template_name = 'djangogramm/create_post.html'

    def form_valid(self, form):
        post = Post(user=self.request.user,
                    text=form.cleaned_data['text'])
        post.save()
        images = self.request.FILES.getlist('images')
        if len(images) == 0 or len(images) > 5:
            raise ValidationError('You can upload up to 5 images. At least 1 is required.')
        save_image_to_post(post, images)
        save_tags_to_post(post, form.cleaned_data['text'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('user', kwargs={'user_slug': self.request.user.slug})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


def validate_email(request):
    return render(request, 'djangogramm/validate.html')


def set_active(request, username, validation_key):
    user = User.objects.get(username=username)
    if user.validation_key == validation_key and user.is_active is False:
        user.is_active = True
        user.save()
        return HttpResponseRedirect(reverse('login'))
    else:
        return render(request, 'djangogramm/404.html', status=404)


def post_like(request):
    post_id = request.POST['post_id']
    user_id = request.POST['user_id']
    if user_id == 'None':
        return JsonResponse(status=500, data={})
    post = Post.objects.get(id=post_id)
    user = User.objects.get(id=user_id)
    is_liked = post.likes.filter(id=user_id).first()
    if is_liked:
        post.likes.remove(user)
    else:
        post.likes.add(user)
    return JsonResponse(data={'status': 200, 'number_likes': post.likes.count()})


def noscript(request):
    return render(request, 'djangogramm/noscript.html')