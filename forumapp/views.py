from django.shortcuts import render
from django.views import generic
from . import models
# Create your views here.
class ChannelView(generic.ListView):
    model = models.Channel
    template_name = 'forumapp/channel.html'
    queryset = Channel.objects.all()
    context_object_name = 'channel_list'

class ThreadView(generic.DetailView, channel_id):
    model = models.Thread
    template_name = 'forumapp/thread.html'
    queryset = Thread.objects.filter(channel_id=channel_id)
    context_object_name = 'thread_list'

class CommentView(generic.DetailView, thread_id):
    model = models.Comment
    template_name = 'forumapp/comment.html'
    queryset = Comment.objects.filter(thread_id=thread_id)
    context_object_name = 'comment_list'
