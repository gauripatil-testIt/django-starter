from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TaskForm
from .models import Task
from .services import send_task_assigned_email


def home(request):
    return render(request, 'core/home.html')


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            send_task_assigned_email(task)
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm()
    return render(request, 'core/task_form.html', {'form': form})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    previous_assignee = task.assignee
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            send_task_assigned_email(task, previous_assignee=previous_assignee)
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'core/task_form.html', {'form': form})


def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'core/task_detail.html', {'task': task})
