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
    return Thread.objects.get(channel__channel_name=channel_name, thread_id=thread_id).owner.username == username

@register.filter
def get_thread_name(kwargs):
    channel_name = kwargs['channel']
    thread_id = kwargs['thread']
    return Thread.objects.get(channel__channel_name=channel_name,thread_id=thread_id).thread_name

#Custom filter for comments to return the thread they belong to's description
@register.filter
def description(kwargs):
    channel_name = kwargs['channel']
    thread_id = kwargs['thread']
    return Thread.objects.get(channel__channel_name=channel_name,thread_id=thread_id).description
