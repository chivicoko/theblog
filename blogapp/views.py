from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm, RegisterForm, CustomAuthenticationForm, QuestionForm
from .models import Post, Question
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import User, Group

import requests
from django.http import JsonResponse
from django.conf import settings


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'blogapp/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'blogapp/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def fetch_jobs(request):
    try:
        url = "http://api.adzuna.com:80/v1/api/jobs/gb/search/1"
        params = {
            'app_id': settings.ADZUNA_APP_ID,
            'app_key': settings.ADZUNA_APP_KEY,
            'results_per_page': 20,
            'what': 'python-django developer',
            'what_exclude': 'java',
            'where': 'london',
            'sort_by': 'salary',
            'salary_min': 5000,
            'full_time': 1,
            'permanent': 1,
            'content-type': 'application/json'
        }
        response = requests.get(url, params=params)
        return response.json()
    except:
        messages.error(request, 'Failed to fetch jobs. Please check your internet connection.')

def fetch_jobs_view(request):
    jobs = fetch_jobs(request)
    return JsonResponse(jobs)

def home(request):
    posts = Post.objects.all()
    questions = Question.objects.all()
    jobs = fetch_jobs(request)
    return render(request, 'blogapp/home.html', {'posts': posts, 'questions':questions, 'jobs':jobs})

@login_required
@permission_required("blogapp.add_question", login_url="login", raise_exception=True)
def teacher(request):
    posts = Post.objects.all()
    return render(request, 'blogapp/teacher.html', {'posts': posts})

@login_required
def new_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            return redirect('success')
        else:
            messages.error(request, 'Failed to add question. Please correct the errors below.')
    else:
        form = QuestionForm()
    return render(request, 'blogapp/add_question.html', {'form': form})

@login_required
def add_test(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('success')
        else:
            messages.error(request, 'Failed to add question. Please correct the errors below.')
    else:
        form = PostForm()
    return render(request, 'blogapp/add_test.html', {'form': form})

@login_required
def questions_tests(request):
    return render(request, 'blogapp/questions_tests.html')

@login_required
def past_questions(request):
    questions = Question.objects.all()
    return render(request, 'blogapp/past_questions.html', {'questions': questions})

@login_required
def subjects(request):
    posts = Post.objects.all()
    return render(request, 'blogapp/subjects.html', {'posts': posts})

# @login_required
def blog(request):
    posts = Post.objects.all()
    
    if request.method == "POST":
        post_id = request.POST.get('post-id')
        user_id = request.POST.get('user-id')

        if post_id:
            post = Post.objects.filter(id=post_id).first()
            if post and (post.author == request.user or request.user.has_perm("blogapp.delete_post")):
                post.delete()
        elif user_id:
            user = User.objects.filter(id=user_id).first()
            if user and request.user.is_staff:
                try:
                    group = Group.objects.get(name='Default')
                    group.user_set.remove(user)
                except:
                    pass

                try:
                    group = Group.objects.get(name='Quasi Admin')
                    group.user_set.remove(user)
                except:
                    pass

        
    return render(request, 'blogapp/blog.html', {'posts': posts})

@login_required
@permission_required("blogapp.add_post", login_url="login", raise_exception=True)
def new_blog_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('success')
        else:
            messages.error(request, 'Failed to create post. Please correct the errors below.')
    else:
        form = PostForm()
    return render(request, 'blogapp/post.html', {'form': form})

@login_required
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'blogapp/post_detail.html', {'post': post})

@login_required
def success(request):
    questions = Question.objects.all()
    return render(request, 'blogapp/success.html')
