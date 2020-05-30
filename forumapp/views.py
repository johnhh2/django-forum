from django.shortcuts import render
from django.views import generic
from .models import Channel, Thread, Comment

# Create your views here.
class ChannelView(generic.ListView):
    model = Channel
    template_name = 'forumapp/channel.html'
    slug_field = 'channel_name'
    slug_url_kwords = 'channel_name'
    queryset = Channel.objects.all()
    context_object_name = 'channel_list'

class ThreadView(generic.DetailView):
    model = Thread
    template_name = 'forumapp/thread.html'
    slug_field = 'channel_name'
    #slug_url_kwords = 'channel_name'
    queryset = Thread.objects.all()
    context_object_name = 'thread_list'
    def get_object(self):
        return Thread.objects.filter(channel_name=self.kwargs.get('channel_name'))

class CommentView(generic.DetailView):
    model = Comment
    template_name = 'forumapp/comment.html'
    slug_field = 'comment_name'
    slug_url_kwords = 'comment_name'
    queryset = Comment.objects.all()
    context_object_name = 'comment_list'
    def get_object(self):
        return Comment.objects.filter(channel_name=self.kwargs.get('channel_name'), thread_id=self.kwargs.get('thread_id'))
