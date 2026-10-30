from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_task_assigned_email(task, *, previous_assignee=None) -> int:
    if task.assignee is None:
        return 0
    if task.assignee == task.owner:
        return 0
    if previous_assignee == task.assignee:
        return 0

    body = render_to_string(
        'emails/task_assigned.txt',
        {
            'task': task,
            'task_url': f'/tasks/{task.pk}/',
        },
    )
    return send_mail(
        subject=f'Task assigned: {task.title}',
        message=body,
        from_email=None,
        recipient_list=[task.assignee.email],
    )
