import json, datetime, dateutil.tz
from django import template
from django.utils import timezone
from forumapp.models import Channel, Thread, Comment

register = template.Library()

#Create filter for comments to check if their publish date is within 24 hours before now.
@register.filter
def is_recent(comment):
    return comment.is_recent()

@register.filter
def format_date(date):
    localtz = dateutil.tz.tzlocal()
    localoffset = localtz.utcoffset(datetime.datetime.now(localtz))
    tz = int(localoffset.total_seconds() / 3600)
    time_diff = timezone.now() - date
    if time_diff > datetime.timedelta(days=365.25):
        return str(date.month) + "/" + str(date.day) + "/" + str(date.year)
    elif time_diff > datetime.timedelta(days=30):
        return str(date.month) + "/" + str(date.day) + " " + str(date.hour + tz) + ":" + str(date.minute)
    elif time_diff > datetime.timedelta(days=7):
        pass
    elif time_diff > datetime.timedelta(days=1):
        pass
    else:
        pass

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

@register.filter
def is_moderator(kwargs, user):
    channel_name = kwargs['channel']
    thread_id = kwargs['thread']

    thread = Thread.objects.filter(channel__channel_name=channel_name, thread_id=thread_id)
    if thread.exists():
        thread = thread.get()
        if user == thread.channel.owner:
            return True
        else:
            return user.get_username() in json.loads(thread.channel.moderators)

    return False
