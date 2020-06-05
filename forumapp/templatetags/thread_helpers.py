import json
from django import template
from forumapp.models import Channel, Thread, Comment

register = template.Library()

#Create filter for threads to see if they are owned by the user passed in
@register.filter
def is_owned_by(channel_name, username):
    return Channel.objects.get(channel_name=channel_name).owner.username == username

#Custom filter for threads to return the channel they belong to's description
@register.filter
def description(channel_name):
    if Channel.objects.filter(channel_name=channel_name).exists():
        return Channel.objects.get(channel_name=channel_name).description
