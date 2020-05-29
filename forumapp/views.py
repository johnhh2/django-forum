from django.shortcuts import render
from django.views import generic

# Create your views here.
class ChannelView(generic.ListView):
    model = Channel
    template_name = 'forumapp/channel.html'

class ThreadView(generic.DetailView):
    model = Thread
    template_name = 'forumapp/thread.html'

class CommentView(generic.DetailView):
    model = Comment
    template_name = 'forumapp/comment.html'
