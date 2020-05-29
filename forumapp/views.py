from django.shortcuts import render
from django.views import generic
from .models import Channel, Thread, Comment

# Create your views here.
class ChannelView(generic.ListView):
    model = Channel
    template_name = 'forumapp/channel.html'
    queryset = Channel.objects.all()
    context_object_name = 'channel_list'

class ThreadView(generic.DetailView):
    model = Thread
    template_name = 'forumapp/thread.html'
    queryset = Thread.objects.all()
    context_object_name = 'thread_list'

class CommentView(generic.DetailView):
    model = Comment
    template_name = 'forumapp/comment.html'
    queryset = Comment.objects.all()
    context_object_name = 'comment_list'
