import json, datetime
from django import template
from django.utils import timezone
from forumapp.models import Channel, Thread, Comment

register = template.Library()

#Create filter for comments to check if their publish date is within 24 hours before now.
@register.filter
def is_recent(comment):
    return comment.is_recent()

@register.filter
def how_recent(date):
    time_diff = timezone.now() - date
    if time_diff > datetime.timedelta(days=365.25):
        return "year"
    elif time_diff > datetime.timedelta(days=30):
        return "month"
    elif time_diff > datetime.timedelta(days=7):
        return "week"
    elif time_diff > datetime.timedelta(days=1):
        return "day"
    elif timezone.now() > date:
        return "new"
    else:
        return "future"

#Create filter for comments to see if they are owned by the user passed in
@register.filter
def is_owned_by(kwargs, username):
    channel_name = kwargs['channel']
    thread_id = kwargs['thread']

    thread = Thread.objects.filter(channel__channel_name=channel_name, thread_id=thread_id)
    if thread.exists():
        return thread.get().owner == user
    else:
        return ''

@register.filter
def get_thread_name(kwargs):
    channel_name = kwargs['channel']
    thread_id = kwargs['thread']

    thread = Thread.objects.filter(channel__channel_name=channel_name, thread_id=thread_id)
    if thread.exists():
        return thread.get().thread_name
    else:
        return ''

#Custom filter for comments to return the thread they belong to's description
@register.filter
def description(kwargs):
    channel_name = kwargs['channel']
    thread_id = kwargs['thread']

    thread = Thread.objects.filter(channel__channel_name=channel_name, thread_id=thread_id)
    if thread.exists():
        return thread.get().description
    else:
        return ''
