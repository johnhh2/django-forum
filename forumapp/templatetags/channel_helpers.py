import string
from django import template

register = template.Library()

#Create filter for threads to see if they are owned by the user passed in
@register.filter
def remove_hyphens(channel_name):
    return channel_name.replace('-', ' ')

