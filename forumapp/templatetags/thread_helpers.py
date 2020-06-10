import json
from django import template
from forumapp.models import Channel, Thread, Comment

register = template.Library()

#Create filter for threads to see if they are owned by the user passed in
@register.filter
def is_owned_by(channel_name, username):
    channel = Channel.objects.filter(channel_name=channel_name)
    if channel.exists():
        return owner.get().get_username() == username
    else:
        return False

#Custom filter for threads to return the channel they belong to's description
@register.filter
def description(channel_name):
    channel = Channel.objects.filter(channel_name=channel_name)
    if channel.exists():
        return channel.get().description
    else:
        return ''

@register.filter
def is_moderator(kwargs, user):
    channel = Channel.objects.filter(channel_name=kwargs.get('channel'))
    if channel.exists():
        channel = channel.get()
        if user.get_username() == channel.owner.get_username:
            return True
        else:
            return user.get_username() in json.loads(channel.moderators)

    return False
