from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django.utils import timezone
from django.urls import reverse
from .models import Channel, Thread, Comment
from .forms import ChannelForm, ThreadForm, CommentForm

class ViewMixin(generic.base.ContextMixin):
    def get_context_data(self, **kwargs):
        context = super(ViewMixin, self).get_context_data(**kwargs)
        context['form'] = self.form_class(initial=self.initial)
        context[self.context_object_name] = self.get_object()
        return context

# Create your views here.
class ChannelView(ViewMixin, generic.ListView):
    model = Channel
    template_name = 'forumapp/channel.html'

    form_class = ChannelForm
    initial = {'key': 'value'}

    queryset = Channel.objects.all()
    context_object_name = 'channel_list'

    def get_object(self):
        return Channel.objects.all()

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            channel_name = form.cleaned_data.get('channel_name')
            description = form.cleaned_data.get('description')
            
            if len(channel_name) > 3:
                if len(description) > 5:
                    owner = request.user

                    if owner.is_authenticated:

                        channel = Channel(channel_name=channel_name, description=description, owner=owner)
                        
                        try:
                            channel.save()
                            return HttpResponseRedirect(reverse('forumapp:thread', kwargs={'channel': channel_name}))
                        except:
                            messages.error(request, "Channel already exists with that name.")

                    else:
                        messages.error(request, "Please log in to create channels")
                        
                else:
                    messages.error(request, "Channel description must be at least 6 characters")

            else:
                messages.error(request, "Channel name must be at least 3 characters")

        else:
            messages.error(request, "Invalid input. Channel name must contain hyphens in place of whitespace")
        
        return HttpResponseRedirect(self.request.path_info)

class ThreadView(ViewMixin, generic.DetailView):
    model = Thread
    template_name = 'forumapp/thread.html'

    form_class = ThreadForm
    initial = {'key': 'value'}

    queryset = Thread.objects.all()
    context_object_name = 'thread_list'

    # Return querylist of threads in the given channel
    def get_object(self):
        c_name = self.kwargs.get('channel')

        return Thread.objects.filter(channel__channel_name=c_name)

    def post(self, request, *args, **kwargs):

        if 'delete' in request.POST:
            Channel.objects.get(channel_name=self.kwargs.get('channel')).delete()

            return HttpResponseRedirect(reverse('forumapp:channel'))

        elif 'back' in request.POST:
            return HttpResponseRedirect(reverse('forumapp:channel'))
        
        elif 'create' in request.POST:
            form = self.form_class(request.POST)
            if form.is_valid():
                thread_name = form.cleaned_data.get('thread_name')
                description = form.cleaned_data.get('description')
                
                if len(form.cleaned_data.get('thread_name')) > 5:

                    if len(form.cleaned_data.get('description')) > 5:

                        channel = Channel.objects.get(channel_name=self.kwargs.get('channel'))
                        owner = request.user

                        if owner.is_authenticated:
                            
                            thread = Thread(channel=channel, thread_name=thread_name, description=description, owner=owner)
                            try:
                                thread.save()

                                #Update recent_date of the channel
                                date = timezone.now()
                                channel.recent_date = date
                                channel.save()

                                return HttpResponseRedirect(reverse('forumapp:comment', kwargs={'channel': channel.channel_name, 'thread': thread.thread_id}))

                            except:
                                messages.error(request, "Thread already exists with that name.")

                        else:
                            messages.error(request, "Please log in to create threads")
                
                    else:
                        messages.error(request, "Thread description must be at least 6 characters")
                
                else:
                    messages.error(request, "Thread name must be at least 6 characters")

            else:
                messages.error(request, "Invalid input")
        
        return HttpResponseRedirect(self.request.path_info)

class CommentView(ViewMixin, generic.DetailView):
    model = Comment
    template_name = 'forumapp/comment.html'

    form_class = CommentForm
    initial = {'key': 'value'}

    queryset = Comment.objects.all()
    context_object_name = 'comment_list'

    # Return querylist of comments in the given channel and thread
    def get_object(self):
        t_id = self.kwargs.get('thread')
        c_name = self.kwargs.get('channel')

        return Comment.objects.filter(thread__thread_id=t_id, thread__channel__channel_name=c_name)

    def post(self, request, *args, **kwargs):

        if 'delete' in request.POST:
            Thread.objects.get(thread_id=self.kwargs.get('thread'), channel__channel_name=self.kwargs.get('channel')).delete()
        
            return HttpResponseRedirect(reverse('forumapp:thread', kwargs={'channel': self.kwargs.get('channel')}))

        elif 'back' in request.POST:
            return HttpResponseRedirect(reverse('forumapp:thread', kwargs={'channel': self.kwargs.get('channel')}))
        
        elif 'create' in request.POST:
            form = self.form_class(request.POST)
            if form.is_valid():
                text = form.cleaned_data.get('text')
                
                if len(text) > 5:
                    thread = Thread.objects.get(channel__channel_name=self.kwargs.get('channel'), thread_id=self.kwargs.get('thread'))
                    owner = request.user

                    if owner.is_authenticated:
                        comment = Comment(thread=thread, text=text, owner=owner)
                        
                        try:
                            comment.save()
                        
                            #Update recent_date of the channel and thread
                            date = timezone.now()
                            thread.channel.recent_date = date
                            thread.channel.save()

                            thread.recent_date = date
                            thread.save()
                            
                            return HttpResponseRedirect(self.request.path_info)

                        except:
                            messages.error(request, "Comment already exists with that name.")

                    else:
                        messages.error(request, "Please log in to create comments")

                else:
                    messages.error(request, "Comments must be at least 6 characters")

            else:
                messages.error(request, "Invalid input")
 
        return HttpResponseRedirect(self.request.path_info)
