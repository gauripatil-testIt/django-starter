from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import urlencode

from .models import Task


@login_required
def task_list(request):
    tasks = Task.objects.filter(owner=request.user)

    status = request.GET.get('status', '')
    if status in Task.Status.values:
        tasks = tasks.filter(status=status)
    else:
        status = ''

    q = request.GET.get('q', '').strip()
    if q:
        tasks = tasks.filter(title__icontains=q)

    current_sort = request.GET.get('sort', 'asc')
    if current_sort == 'desc':
        tasks = tasks.order_by(F('due_date').desc(nulls_last=True))
        next_sort = 'asc'
    else:
        current_sort = 'asc'
        tasks = tasks.order_by(F('due_date').asc(nulls_last=True))
        next_sort = 'desc'

    sort_query = {'sort': next_sort}
    if status:
        sort_query['status'] = status
    if q:
        sort_query['q'] = q
    sort_url = f"{reverse('task_list')}?{urlencode(sort_query)}"

    context = {
        'tasks': tasks,
        'status_choices': Task.Status.choices,
        'current_status': status,
        'current_q': q,
        'current_sort': current_sort,
        'sort_url': sort_url,
    }
    return render(request, 'tasks/task_list.html', context)
