from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    return render(request, "home.html")


def signup(request):
    if request.method == "GET":
        return render(request, "signup.html", {"form": UserCreationForm})
    else:
        if request.POST["password1"] == request.POST["password2"]:

            try:
                user = User.objects.create_user(
                    request.POST["username"], password=request.POST["password1"]
                )
                user.save()
                login(request, user)
                return redirect("tasks")
            except IntegrityError:
                return render(
                    request,
                    "signup.html",
                    {
                        "form": UserCreationForm,
                        "error": "User already exists",
                    },
                )

        return render(
            request,
            "signup.html",
            {
                "form": UserCreationForm,
                "error": "Passwords did not match",
            },
        )


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, dateCompleted__isnull=True)
    return render(request, "tasks.html", {"tasks": tasks})


@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(
        user=request.user, dateCompleted__isnull=False
    ).order_by("-dateCompleted")
    return render(request, "tasks.html", {"tasks": tasks})


@login_required
def create_task(request):
    if request.method == "GET":
        return render(request, "create_task.html", {"form": TaskForm})
    else:
        try:
            new_task = TaskForm(request.POST)
            new_task.instance.user = request.user
            new_task.save()
            return redirect("tasks")
        except ValueError:
            return render(
                request,
                "create_task.html",
                {
                    "form": TaskForm,
                    "error": "Invalid data",
                },
            )


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)

    if request.method == "GET":
        print("hello word")
        form = TaskForm(instance=task)
        return render(request, "task_detail.html", {"task": task, "form": form})
    else:
        try:
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect("tasks")
        except ValueError:
            return render(
                request,
                "task_detail.html",
                {
                    "task": task,
                    "form": TaskForm,
                    "error": "Invalid data, isn't possible to update the task",
                },
            )


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":
        task.dateCompleted = timezone.now()
        task.save()
        return redirect("tasks")


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":
        task.delete()
        return redirect("tasks")


@login_required
def signout(request):
    logout(request)
    return redirect("home")


def signin(request):
    if request.method == "GET":
        return render(request, "signin.html", {"form": AuthenticationForm})
    else:
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )

        if user is None:
            return render(
                request,
                "signin.html",
                {
                    "form": AuthenticationForm,
                    "error": "User or password is incorrect",
                },
            )
        else:
            login(request, user)
            return redirect("tasks")
