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

    # Return querylist of threads in the given channel
    def get_object(self):
        c_name = self.kwargs.get('channel')
        if Channel.objects.filter(channel_name=c_name).exists():
            return Thread.objects.filter(channel__channel_name=c_name)
        else: #TODO: 404
            return Thread.objects.none()

class CommentView(generic.DetailView):
    model = Comment
    template_name = 'forumapp/comment.html'
    queryset = Comment.objects.all()
    context_object_name = 'comment_list'

    # Return querylist of comments in the given channel and thread
    def get_object(self):
        t_id = self.kwargs.get('thread')
        c_name = self.kwargs.get('channel')

        if Thread.objects.filter(thread_id=t_id).exists() and Channel.objects.filter(channel_name=c_name):
            return Comment.objects.filter(thread__thread_id=t_id, thread__channel__channel_name=c_name)
        else: #TODO: 404
            return Comment.objects.none()
