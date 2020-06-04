from django.contrib import messages
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils import timezone
from django.urls import reverse
from .models import UserSettings, Channel, Thread, Comment
from .forms import UserSettingsForm, ChannelForm, ThreadForm, CommentForm

class ViewMixin(generic.base.ContextMixin):
    initial = {'key': 'value'}

    def get_context_data(self, **kwargs):
        context = super(ViewMixin, self).get_context_data(**kwargs)

        if hasattr(self, 'form_class'):
            context['form'] = self.form_class(initial=self.initial)
        if hasattr(self, 'context_object_name'):
            context[self.context_object_name] = self.get_object()
        return context

# Show the settings menu
class UserSettingsView(ViewMixin, generic.DetailView):
    model = UserSettings
    template_name = 'forumapp/user_settings.html'

    form_class = UserSettingsForm

    queryset = UserSettings.objects

    def get_object(self):
        if self.request.user.is_authenticated():
            user = self.queryset.filter(user__username=self.request.user)
            if user.exists():
                return user.get()
            else:
                self.queryset.create(user=self.request.user)

        return self.queryset.none()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        return super(UserSettingsView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if 'save' in request.POST:
            form = self.form_class(request.POST, instance=self.object)

            if form.is_valid():
                form.save()

            else:
                messages.error(request, "Invalid input")

        return HttpResponseRedirect(self.request.path_info)

# Create your views here.
class ChannelView(ViewMixin, generic.ListView):
    model = Channel
    template_name = 'forumapp/channel.html'

    form_class = ChannelForm

    queryset = Channel.objects
    context_object_name = 'channel_list'

    def get_object(self, exclude=None):
        return self.queryset.all()

    def post(self, request, *args, **kwargs):
        owner = request.user
        channel = Channel(owner=owner)
        form = self.form_class(request.POST, instance=channel)

        if form.is_valid():
            channel_name = form.cleaned_data.get('channel_name')
            description = form.cleaned_data.get('description')

            if len(channel_name) > 3:
                if len(description) > 5:

                    if owner.is_authenticated:

                        try:
                            channel.save()
                            return HttpResponseRedirect(reverse('forumapp:thread', kwargs={'channel': channel_name}))
                        except:
                            messages.error(request, "Channel already exists with that name.")

                    else:
                        messages.error(request, "Please log in to create channels.")

                else:
                    messages.error(request, "Channel description must be at least 6 characters.")

            else:
                messages.error(request, "Channel name must be at least 3 characters.")

        else:
            messages.error(request, "Invalid input. Channel name must contain hyphens in place of whitespace and cannot contain symbols.")

        return HttpResponseRedirect(self.request.path_info)

class ThreadView(ViewMixin, generic.DetailView):
    model = Thread
    template_name = 'forumapp/thread.html'

    form_class = ThreadForm

    queryset = Thread.objects
    context_object_name = 'thread_list'

    # Return querylist of threads in the given channel
    def get_object(self):
        c_name = self.kwargs.get('channel')

        return self.queryset.filter(channel__channel_name=c_name)

    def post(self, request, *args, **kwargs):
        channel = get_object_or_404(Channel, channel_name=self.kwargs.get('channel'))
 
        if 'delete' in request.POST:
            channel.delete()

            return HttpResponseRedirect(reverse('forumapp:channel'))

        elif 'back' in request.POST:
            return HttpResponseRedirect(reverse('forumapp:channel'))

        elif 'create' in request.POST:
            owner = request.user

            thread = Thread(channel=channel, owner=owner)
            thread.save()
            form = self.form_class(request.POST, instance=thread)

            if form.is_valid():
                thread_name = form.cleaned_data.get('thread_name')
                description = form.cleaned_data.get('description')

                if len(thread_name) > 5:

                    if len(description) > 5:

                        if owner.is_authenticated:
                            try:
                                form.save()

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

    queryset = Comment.objects
    context_object_name = 'comment_list'

    # Return querylist of comments in the given channel and thread
    def get_object(self):
        t_id = self.kwargs.get('thread')
        c_name = self.kwargs.get('channel')

        return self.queryset.filter(thread__thread_id=t_id, thread__channel__channel_name=c_name)

    def post(self, request, *args, **kwargs):
        thread = get_object_or_404(Thread, channel__channel_name=self.kwargs.get('channel'), thread_id=self.kwargs.get('thread'))

        if 'delete' in request.POST:
            thread.delete()

            return HttpResponseRedirect(reverse('forumapp:thread', kwargs={'channel': self.kwargs.get('channel')}))

        elif 'back' in request.POST:
            return HttpResponseRedirect(reverse('forumapp:thread', kwargs={'channel': self.kwargs.get('channel')}))

        elif 'create' in request.POST:
            owner = request.user
            comment = Comment(thread=thread, owner=owner)
            comment.save()
            form = self.form_class(request.POST, instance=comment)

            if form.is_valid():
                text = form.cleaned_data.get('text')

                if len(text) > 5:

                    if owner.is_authenticated:

                        try:
                            form.save()

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

class UserView(ViewMixin, generic.DetailView):
    model = User
    template_name = 'forumapp/user.html'

    queryset = User.objects
    def get_object(self):
        username = self.kwargs.get('username')
        if self.queryset.filter(username=username).exists():
            return self.queryset.get(username=username)

        return self.queryset.none()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(UserView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        if 'admin_ban' in request.POST:

            user = queryset.filter(username=username)
            if user.exists():
                user = user.get()
                user.is_active = False
                user.save()
                return HttpResponseRedirect(self.request.path_info)
            else:
                return Http404("User does not exist.")

        elif 'admin_unban' in request.POST:
            user = queryset.filter(username=username)
            if user.exists():
                user = user.get()
                user.is_active = True
                user.save()
                return HttpResponseRedirect(self.request.path_info)
            else:
                return Http404("User does not exist.")
