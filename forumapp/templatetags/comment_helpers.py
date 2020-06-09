import json
from django import template
from forumapp.models import Channel, Thread, Comment

register = template.Library()

#Create filter for comments to check if their publish date is within 24 hours before now.
@register.filter
def is_recent(comment):
    return comment.is_recent()

#Create filter for comments to see if they are owned by the user passed in
@register.filter
def is_owner(kwargs, username):
    channel_name = kwargs['channel']
    thread_id = kwargs['thread']
    
    thread = Thread.objects.filter(channel__channel_name=channel_name, thread_id=thread_id)
    if thread.exists():
        return thread.get().owner.get_username == username
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
def is_moderator(user, channel):
    if user.get_username == channel.owner.get_username:
        return True
    else:
        return user.get_username in json.loads(channel.moderators)
