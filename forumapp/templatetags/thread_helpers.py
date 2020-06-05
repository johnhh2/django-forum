import json
from django import template
from forumapp.models import Channel, Thread, Comment

register = template.Library()

#Create filter for threads to see if they are owned by the user passed in
@register.filter
def is_owned_by(channel_name, username):
    return Channel.objects.get(channel_name=channel_name).owner.username == username
