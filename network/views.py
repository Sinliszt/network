from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
import json
from django.views.decorators.csrf import csrf_exempt


from .models import User, Post, Follow

def index(request):

    if request.method == "POST":
        content = request.POST.get("content")

        if content:
            Post.objects.create(user=request.user, content=content, timestamp=now())
        return redirect("index")
    
    posts = Post.objects.all().order_by("-timestamp")
    paginator=Paginator(posts,10)
    page_number = request.GET.get("page")
    page_object = paginator.get_page(page_number)
    liked_posts = []

    if request.user.is_authenticated:
        liked_posts = Post.objects.filter(likes=request.user).values_list("id", flat=True)

    return render(request, "network/index.html", {
        "page_object": page_object,
        "posts": posts,
        "liked_posts": liked_posts,
    })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    
    followers = Follow.objects.filter(following=user_profile).count()
    following = Follow.objects.filter(follower=user_profile).count()

    is_following = request.user.is_authenticated and Follow.objects.filter(follower=request.user, following=user_profile).exists()

    posts = Post.objects.filter(user=user_profile).order_by("-timestamp")

    paginator = Paginator(posts,10)
    page_number = request.GET.get("page")
    page_object = paginator.get_page(page_number)

    return render (request, "network/profile.html", {
        "page_object": page_object,
        "user_profile": user_profile,
        "is_following": is_following,
        "followers": followers,
        "following": following,
    })

@login_required
def follow(request,username):
    user_profile = get_object_or_404(User, username=username)

    if request.user == user_profile:
        return JsonResponse({"error": "You cannot follow yourself."}, status=400)

    if request.method == "POST":

        follow_instance = Follow.objects.filter(follower=request.user, following=user_profile).first()

        if follow_instance:
            follow_instance.delete()
            following_status = False
        else:
            Follow.objects.create(follower=request.user, following=user_profile)
            following_status = True

        followers_count = Follow.objects.filter(following=user_profile).count()


        return JsonResponse ({
            "followers_count": followers_count,
            "following_status": following_status,
        })

    return JsonResponse({"Error: ": "Invalid request method."}, status=405)


@login_required
def edit_post(request, post_id):

    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            post = Post.objects.get(id=post_id)
            
            if post.user != request.user:
                return JsonResponse({"error": "You are not allowed to edit this post."}, status=403)

            new_content = data.get("content", "").strip()
            if not new_content:
                return JsonResponse({"error": "Post content cannot be empty."}, status=400)

            post.content = new_content
            post.save()
            
            return JsonResponse({
                "content": post.content, 
                "message": "Post updated successfully.",
            })

        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)



@login_required
def like_post(request, post_id):
    if request.method == "PUT":
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return JsonResponse({"likes": post.likes.count()})
    return HttpResponseBadRequest("Invalid request")

@login_required
def follow_view(request):
    following_users = Follow.objects.filter(follower=request.user).values_list("following", flat=True)

    posts = Post.objects.filter(user__id__in=following_users).order_by("-timestamp")
    paginator=Paginator(posts,10)
    page_number = request.GET.get("page")
    page_object = paginator.get_page(page_number)
    liked_posts = []

    if request.user.is_authenticated:
        liked_posts = Post.objects.filter(likes=request.user).values_list("id", flat=True)

    return render(request, "network/following.html", {
        "posts": posts,
        "page_object": page_object,
        "liked_posts": liked_posts,
    })