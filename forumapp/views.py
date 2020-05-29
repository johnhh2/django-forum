from django.shortcuts import render
from django.views import generic
from . import models
# Create your views here.
class ChannelView(generic.ListView):
    model = models.Channel
    template_name = 'forumapp/channel.html'

    def get_queryset(request):
        return Channel.objects.all()

class ThreadView(generic.DetailView, channel_id):
    model = models.Thread
    template_name = 'forumapp/thread.html'

    def get_queryset(request):
        return Thread.objects.filter(channel_id__eq=channel_id)

class CommentView(generic.DetailView, thread_id):
    model = models.Comment
    template_name = 'forumapp/comment.html'

    def get_queryset(request):
        return Comment.objects.filter(thread_id__eq=thread_id)
