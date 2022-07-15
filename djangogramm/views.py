from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse, Http404
from .models import *
from django.views.generic import CreateView, ListView, DetailView, FormView
from .forms import *
from .utils import *
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
        send_email(user.email, user.username)
        return reverse('validate')


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
        return reverse('user', kwargs={'user_slug': self.request.user.slug})

    def form_valid(self, form):
        user = self.request.user
        profile_photo = form.cleaned_data.get('profile_photo', None)
        if profile_photo:
            user.profile_photo = self.request.FILES['profile_photo']
        user.bio = form.cleaned_data['bio']
        user.save()
        return super().form_valid(form)

    def get_initial(self):
        return {'bio': self.request.user.bio}

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class CreatePost(LoginRequiredMixin, FormView):
    form_class = CreatePostForm
    template_name = 'djangogramm/create_post.html'

    def form_valid(self, form):
        post = Post(user=self.request.user,
                    text=form.cleaned_data['text'])
        post.save()
        images = self.request.FILES.getlist('images')
        save_image_to_post(post, images)
        save_tags_to_post(post, form.cleaned_data['text'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('user', kwargs={'user_slug': self.request.user.slug})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        print(form.errors)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


def validate_email(request):
    return render(request, 'djangogramm/validate.html')


def set_active(request, username, key):
    user = User.objects.get(username=username)
    signer = Signer(salt='django')
    if user.email == signer.unsign(key) and user.is_active is False:
        user.is_active = True
        user.save()
    return HttpResponseRedirect(reverse('login'))


def post_like(request):
    post_id = request.POST['post_id']
    post = Post.objects.get(id=post_id)
    user = request.user
    is_liked = post.likes.filter(id=user.pk).first()
    if is_liked:
        post.likes.remove(user)
    else:
        post.likes.add(user)
    return JsonResponse(data={'status': 200, 'number_likes': post.likes.count()})


def noscript(request):
    return render(request, 'djangogramm/noscript.html')