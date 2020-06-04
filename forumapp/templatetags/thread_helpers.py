from django import template
from forumapp.models import Channel, Thread, Comment

register = template.Library()

#Create filter for threads to see if they are owned by the user passed in
@register.filter
def isownedby(channel_name, username):
    return Channel.objects.get(channel_name=channel_name).owner.username == username
