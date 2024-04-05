from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Post, LikePost, FollowCount
from django.contrib.auth.decorators import login_required
from itertools import chain
import random

# Create your views here.


@login_required(login_url="core:signin")
def index(request):
    username = request.user.username
    user = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=request.user)

    following_list = FollowCount.objects.filter(follower=username)
    following_names_list = []

    # get_names_following
    for users in following_list:
        following_names_list.append(users.user)

    # following_posts
    posts_list = []
    for name in following_names_list:
        post = Post.objects.filter(user=name)
        posts_list.append(post)
    posts = list(chain(*posts_list))

    # suggestion_username_profile_list ,means_all_users_in_db_not_me_and_not_following_users_for_me_finally_i_take_their_profiles

    followoing_users = []
    for name in following_names_list:
        user = User.objects.get(username=name)
        followoing_users.append(user)

    users_all = User.objects.all()

    users_not_in_following = [
        x for x in list(users_all) if x not in list(followoing_users)
    ]

    me = User.objects.filter(username=username)

    users_without_me = [x for x in list(users_not_in_following) if x not in list(me)]

    # randomize_users ,means user selection is random
    random.shuffle(users_without_me)

    ids = []
    for user in users_without_me:
        ids.append(user.pk)

    users_profiles = []
    for id in ids:
        profile = Profile.objects.filter(id_user=id)
        users_profiles.append(profile)

    suggestions_username_profile_list = list(chain(*users_profiles))

    return render(
        request,
        "index.html",
        {
            "user": user,
            "user_profile": user_profile,
            "posts": posts,
            "username": username,
            "suggestions_username_profile_list": suggestions_username_profile_list[:4],
        },
    )


def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "email taken")
                return redirect("http://127.0.0.1:8000/signup/")
            elif User.objects.filter(username=username).exists():
                messages.info(request, "username taken")
                return redirect("http://127.0.0.1:8000/signup/")
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    is_staff=True,
                    is_active=True,
                    is_superuser=True,
                )
                user_login = authenticate(request, username=username, password=password)
                login(request, user_login)

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(
                    user=user_model, id_user=user_model.pk
                )
                new_profile.save()
        else:
            messages.info(request, "password doesn't match.")
            return redirect("http://127.0.0.1:8000/signup/")
    else:
        return render(request, "signup.html")


def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("http://127.0.0.1:8000/")
        else:
            messages.info(request, "invalid credentials")
            return redirect("http://127.0.0.1:8000/signin/")
    else:
        return render(request, "signin.html")


@login_required(login_url="core:signin")
def logedout(request):
    logout(request)
    return redirect("http://127.0.0.1:8000/signin/")


@login_required(login_url="core:signin")
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        if request.FILES.get("image") == None:
            image = user_profile.profile_image
            bio = request.POST["bio"]
            location = request.POST["location"]
            user_profile.profile_image = image
            user_profile.location = location
            user_profile.bio = bio
            user_profile.save()
        if request.FILES.get("image") != None:
            image = request.FILES.get("image")
            bio = request.POST["bio"]
            location = request.POST["location"]
            user_profile.profile_image = image
            user_profile.location = location
            user_profile.bio = bio
            user_profile.save()
        return redirect("http://127.0.0.1:8000/settings")
    else:
        return render(request, "setting.html", {"user_profile": user_profile})


@login_required(login_url="core:signin")
def upload(request):

    if request.method == "POST":
        user = request.user.username
        caption = request.POST["caption"]
        image = request.FILES.get("image_upload")
        new_post = Post.objects.create(user=user, caption=caption, image=image)
        new_post.save()
        return redirect("http://127.0.0.1:8000/")

    return redirect("http://127.0.0.1:8000/")


@login_required(login_url="core:signin")
def like_post(request):

    user = request.user.username
    id_post = request.GET.get("id_post")

    post = Post.objects.get(id=id_post)

    like_filter = LikePost.objects.filter(id_post=id_post, user=user).first()

    if like_filter == None:

        new_like = LikePost.objects.create(user=user, id_post=id_post)
        new_like.save()
        post.no_of_likes += 1
        post.save()
        return redirect("http://127.0.0.1:8000/")

    if like_filter != None:

        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        return redirect("http://127.0.0.1:8000/")


@login_required(login_url="core:signin")
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    posts = Post.objects.filter(user=pk)
    user_post_number = len(posts)

    user_followers = len(FollowCount.objects.filter(user=pk))
    user_following = len(FollowCount.objects.filter(follower=pk))

    user = pk
    follower = request.user.username

    if FollowCount.objects.filter(user=user, follower=follower).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"

    return render(
        request,
        "profile.html",
        {
            "user_profile": user_profile,
            "user_posts": posts,
            "user_object": user_object,
            "user_post_number": user_post_number,
            "user_following": user_following,
            "user_followers": user_followers,
            "button_text": button_text,
        },
    )


@login_required(login_url="core:signin")
def follow(request):

    if request.method == "POST":

        user = request.POST["user"]
        follower = request.POST["follower"]

        if FollowCount.objects.filter(user=user, follower=follower).first():

            delete_follower = FollowCount.objects.get(user=user, follower=follower)
            delete_follower.delete()
            return redirect("http://127.0.0.1:8000/profile/" + user + "/")

        else:

            new_follower = FollowCount.objects.create(user=user, follower=follower)
            new_follower.save()
            return redirect("http://127.0.0.1:8000/profile/" + user + "/")
    else:
        return render(request, "profile.html")


@login_required(login_url="core:signin")
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == "POST":
        username = request.POST["username"]

        users = User.objects.filter(username__icontains=username)

        users_id_list = []
        users_profiles = []

        for user in users:
            users_id_list.append(user.pk)

        for id in users_id_list:
            profile = Profile.objects.filter(id_user=id)
            users_profiles.append(profile)

        username_profile_list = list(chain(*users_profiles))
    return render(
        request,
        "search.html",
        {
            "user_object": user_object,
            "user_profile": user_profile,
            "username": username,
            "username_profile_list": username_profile_list,
        },
    )
