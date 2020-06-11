import json
from django import template
from forumapp.models import Channel, Thread, Comment

register = template.Library()

# filter for threads to see if they are owned by the user passed in
@register.filter
def is_owner(kwargs, user):
    channel = Channel.objects.filter(channel_name=kwargs.get('channel'))

    if channel.exists():
        return channel.get().owner == user
                        
    return False

# filter for threads to see if they are owned/moderated by the user passed in
@register.filter
def is_moderator(kwargs, user):
    channel = Channel.objects.filter(channel_name=kwargs.get('channel'))
            
    if channel.exists():
        channel = channel.get()
        
        if user == channel.owner:
            return True
        
        else:
            return user.get_username() in json.loads(channel.moderators)

    return False

@register.filter
def is_banned_from(user, channel_name):
    channel = Channel.objects.filter(channel_name=channel_name)
            
    # see if user is in list of banned users
    if channel.exists():
        channel = channel.get()
        return user.get_username() in json.loads(channel.banned_users)

    else:
        return False
