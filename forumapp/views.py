import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django.utils import timezone
from django.urls import reverse
from django.forms.models import model_to_dict
from .models import UserSettings, Channel, Thread, Comment
from .forms import UserSettingsForm, ChannelForm, ThreadForm, CommentForm

## Get or create the user's settings (because get_or_create returns an annoying tuple)
def get_or_create_settings(user):
    us = UserSettings.objects.filter(user=user)
    if us.exists():
        return us.get()
    else:
        return UserSettings.objects.create(user=user)
 
## Return whether a user is an owner or moderator of the channel
def is_mod(obj, user):
    # retrieve channel regardless of if we have a channel, thread, or comment
    channel = isinstance(obj, Comment) and obj.thread.channel \
            or (isinstance(obj, Thread) and obj.channel or obj)

    # check if user is owner or moderator
    return user == channel.owner \
            or user.get_username() in json.loads(channel.moderators)

## Return whether a user is an owner of the channel
def is_owner(obj, user):
    # retrieve channel regardless of if we have a channel, thread, or comment
    channel = isinstance(obj, Comment) and obj.thread.channel \
            or (isinstance(obj, Thread) and obj.channel or obj)

    # check if user is owner
    return user == channel.owner

## Automatically lets views attach form and context_objects to the context if defined
class ViewMixin(generic.base.ContextMixin):
    initial = {'key': 'value'}

    def get_context_data(self, **kwargs):
        context = super(ViewMixin, self).get_context_data(**kwargs)

        if hasattr(self, 'form_class'):
            if hasattr(self, 'form_object'):

                #convert object to iterable for form constructor
                context['form'] = self.form_class(initial=model_to_dict(self.object))
            
            else:
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
        if self.request.user.is_authenticated:
            return get_or_create_settings(self.request.user)

        return self.queryset.none()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.form_object = True

        if not hasattr(self, 'object'):
            raise Http404("User does not exist. Are you logged in?")
        
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

# Show the channel settings menu
class ChannelSettingsView(ViewMixin, generic.DetailView):
    model = Channel
    template_name = 'forumapp/channel_settings.html'

    form_class = ChannelForm

    queryset = Channel.objects

    def get_object(self):
        if self.request.user.is_authenticated:
            channel_name = self.kwargs.get('channel')
            channel = self.queryset.filter(channel_name=channel_name)

            if channel.exists():
                return channel.get()

        return self.queryset.none()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.form_object = True

        if not hasattr(self, 'object'):
            raise Http404("User does not exist. Are you logged in?")
        
        # make sure user is owner/mod/admin
        if not (request.user.is_staff or is_mod(self.object, request.user)):
            raise Http404("Insufficient permissions")

        return super(ChannelSettingsView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # make sure user is owner/mod/admin
        if not (request.user.is_staff or is_mod(self.object, request.user)):
            raise Http404("Insufficient permissions")

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

        if 'add_favorite' in request.POST:
            settings = get_or_create_settings(self.request.user)
            favs = json.loads(settings.favorites)
            channel_name = request.POST['channel_name']

            favs.append(channel_name)
            settings.favorites = json.dumps(favs)
            settings.save()

        elif 'remove_favorite' in request.POST:
            settings = get_or_create_settings(self.request.user)
            favs = json.loads(settings.favorites)
            channel_name = request.POST['channel_name']
            
            favs = [c for c in favs if not c == channel_name]
            settings.favorites = json.dumps(favs)
            settings.save()

        elif 'pin' in request.POST:
            channel_name = request.POST['channel_name']
            channel = self.queryset.filter(channel_name=channel_name)
            
            if channel.exists():
                channel = channel.get()
                
                # Require staff status to pin channels
                if request.user.is_staff:
                    channel.pin_date = timezone.now()
                    channel.save()

        elif 'unpin' in request.POST:
            channel_name = request.POST['channel_name']
            channel = self.queryset.filter(channel_name=channel_name)
            
            if channel.exists():
                channel = channel.get()
                
                # Require staff status to unpin channels
                if request.user.is_staff:
                    channel.pin_date = None
                    channel.save()

        elif 'create' in request.POST:
            if not request.user.is_authenticated:
                messages.error(request, "Please log in to create channels.")
                
                return HttpResponseRedirect(self.request.path_info)

            owner = request.user
            channel = Channel(owner=owner)
            form = self.form_class(request.POST, instance=channel)

            if form.is_valid():
                channel_name = form.cleaned_data.get('channel_name')
                description = form.cleaned_data.get('description')

                if len(channel_name) > 3:
                    if len(description) > 5:

                        channel.save()
                        return HttpResponseRedirect(reverse('forumapp:thread', \
                                kwargs={'channel': channel_name}))

                    else:
                        channel.delete()
                        messages.error(request, "Channel description must be at least 6 characters.")

                else:
                    channel.delete()
                    messages.error(request, "Channel name must be at least 4 characters.")

            elif Channel.objects.filter(channel_name=form. data.get('channel_name')).exists():
                messages.error(request, "Channel already exists with that name.")

            else:
                channel.delete()
                messages.error(request, " Channel name must contain hyphens \
                        in place of whitespace and cannot contain symbols.")

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
        
        channel = Channel.objects.filter(channel_name=self.kwargs.get('channel'))
        if not channel.exists():
            return HttpResponseRedirect(reverse('forumapp:channel'))

        channel = channel.get()

        if 'delete_thread' in request.POST:
            thread_id = request.POST['thread_id']
            thread = self.queryset.filter(channel=channel, thread_id=thread_id)
            
            if thread.exists():
                thread = thread.get()

                # Require staff, owner, or mod status to delete threads
                if request.user.is_staff or is_mod(thread, request.user): 

                    thread.delete()

                else:
                    raise Http404("Insufficient permissions.")
            
            else:
                raise Http404("Couldn't find that channel.")

        elif 'delete_channel' in request.POST:

            if request.user.is_staff or is_owner(channel, request.user):
                channel.delete()

                return HttpResponseRedirect(reverse('forumapp:channel'))
            
            else:
                raise Http404("Insufficient permissions.")

            return HttpResponseRedirect(reverse('forumapp:channel'))

        elif 'pin' in request.POST:
            thread_id = request.POST['thread_id']
            thread = self.queryset.filter(channel=channel, thread_id=thread_id)
            
            if thread.exists():
                thread = thread.get()
                
                # Require staff, owner, or mod status to pin threads
                if is_mod(thread, request.user):
                    thread.pin_date = timezone.now()
                    thread.save()
                
                else:
                    raise Http404("Couldn't find that thread.")
            
            else:
                raise Http404("Insufficient permissions.")

        elif 'unpin' in request.POST:
            thread_id = request.POST['thread_id']
            thread = self.queryset.filter(channel=channel, thread_id=thread_id)
            
            if thread.exists():
                thread = thread.get()
                
                # Require staff, owner, or mod status to unpin threads
                if is_mod(thread, request.user):
                    thread.pin_date = None
                    thread.save()
                
                else:
                    raise Http404("Couldn't find that thread.")
            
            else:
                raise Http404("Insufficient permissions.")

        elif 'create' in request.POST:

            if not request.user.is_authenticated:
                messages.error(request, "Please log in to create threads.")
                
                return HttpResponseRedirect(self.request.path_info)

            owner = request.user
            thread = Thread(channel=channel, owner=owner)
            thread.save()
            form = self.form_class(request.POST, instance=thread)

            if form.is_valid():
                thread_name = form.cleaned_data.get('thread_name')
                description = form.cleaned_data.get('description')

                if len(thread_name) > 5:

                    if len(description) > 5:

                        form.save()

                        #Update recent_date of the channel
                        date = timezone.now()
                        channel.recent_date = date
                        channel.save()

                        return HttpResponseRedirect(reverse('forumapp:comment', \
                                kwargs={'channel': channel.channel_name, 'thread': thread.thread_id}))

                    else:
                        thread.delete()
                        messages.error(request, "Thread description must be at least 6 characters.")

                else:
                    thread.delete()
                    messages.error(request, "Thread name must be at least 6 characters.")

            elif Thread.objects.filter(channel=channel, thread_name=form.data.get('thread_name')).exists():
                messages.error(request, "Thread already exists with that name.")

            else:
                thread.delete()
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
        
        thread = Thread.objects.filter(channel__channel_name=self.kwargs.get('channel'), \
                thread_id=self.kwargs.get('thread'))

        if not thread.exists():
            return HttpResponseRedirect(reverse('forumapp:thread', kwargs={'channel': self.kwargs.get('channel')}))

        thread = thread.get()

        if 'delete_comment' in request.POST:
            
            comment_id = request.POST['comment_id']
            comment = self.queryset.filter(thread=thread, comment_id=comment_id)
            
            if comment.exists():
                comment = comment.get()

                # Require staff, owner, or mod status to delete comments
                if request.user.is_staff or is_mod(comment, request.user): 
                    
                    comment.delete()
                
                else:
                    raise Http404("Insufficient permissions.")
            
            else:
                raise Http404("Couldn't find that comment.")

        elif 'delete_thread' in request.POST:

            if request.user.is_staff or is_mod(thread, request.user):
                thread.delete()

                return HttpResponseRedirect(reverse('forumapp:thread', \
                        kwargs={'channel': self.kwargs.get('channel')}))
            
            else:
                raise Http404("Insufficient permissions.")

        elif 'create' in request.POST:

            if not request.user.is_authenticated:
                messages.error(request, "Please log in to create comments.")
                
                return HttpResponseRedirect(self.request.path_info)
            
            owner = request.user
            comment = Comment(thread=thread, owner=owner)
            comment.save()
            form = self.form_class(request.POST, instance=comment)

            if form.is_valid():
                text = form.cleaned_data.get('text')

                if len(text) > 5:

                    form.save()

                    #Update recent_date of the channel and thread
                    date = timezone.now()
                    thread.channel.recent_date = date
                    thread.channel.save()

                    thread.recent_date = date
                    thread.save()

                    return HttpResponseRedirect(self.request.path_info)

                else:
                    comment.delete()
                    messages.error(request, "Comments must be at least 6 characters.")

            else:
                comment.delete()
                messages.error(request, "")

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
        
        if not self.object:
            return HttpResponseRedirect(reverse('forumapp:channel'))
        
        return super(UserView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        user = self.queryset.filter(username=username)
        
        if not user.exists():
            return HttpResponseRedirect(reverse('forumapp:channel'))

        user = user.get()

        if 'admin_ban' in request.POST:
        
            if request.user.is_authenticated and request.user.is_staff:
                user.is_active = False
                user.save()
            
            else:
                raise Http404("User does not exist.")

        elif 'admin_unban' in request.POST:
            
            if request.user.is_authenticated and request.user.is_staff:
                user.is_active = True
                user.save()
            
            else:
                raise Http404("User does not exist.")

        elif 'channel_ban' in request.POST:
            
            if request.user.is_authenticated:
                channel_name = request.POST.get('channel_name')
                channel = Channel.objects.filter(channel_name=channel_name)
                
                if channel.exists():
                    channel = channel.get()

                    if is_mod(channel, request.user):

                        banned_users = json.loads(channel.banned_users)
                        banned_users.append(username)
                        
                        moderators = json.loads(channel.banned_users)
                        moderators = [u for u in moderators if not u == username]
                        
                        channel.banned_users = json.dumps(banned_users)
                        channel.moderators = json.dumps(moderators)
                        channel.save()
                
                    else:
                        raise Http404("Insufficient permissions.")
                
                else:
                    raise Http404("Couldn't find that channel.")

            else:
                raise Http404("User does not exist.")

        elif 'channel_unban' in request.POST:
            
            if request.user.is_authenticated:
                channel_name = request.POST.get('channel_name')
                channel = Channel.objects.filter(channel_name=channel_name)
                
                if channel.exists():
                    channel = channel.get()

                    if is_mod(channel, request.user):
                    
                        banned_users = json.loads(channel.banned_users)
                        banned_users = [u for u in banned_users if not u == username]

                        channel.banned_users = json.dumps(banned_users)
                        channel.save()

                    else:
                        raise Http404("Insufficient permissions.")
                
                else:
                    raise Http404("Couldn't find that channel.")

            else:
                raise Http404("User does not exist.")
        
        elif 'promote_mod' in request.POST:
            
            if request.user.is_authenticated:
                channel_name = request.POST.get('channel_name')
                channel = Channel.objects.filter(channel_name=channel_name)
                
                if channel.exists():
                    channel = channel.get()

                    if is_owner(channel, request.user):

                        if not '"'+username+'"' in channel.banned_users:
                            moderators = json.loads(channel.moderators)
                            moderators.append(username)
                            
                            channel.moderators = json.dumps(moderators)
                            channel.save()
                
                        else:
                            messages.error(request, "Channel-banned users cannot be promoted.")

                    else:
                        raise Http404("Insufficient permissions.")
                
                else:
                    raise Http404("Couldn't find that channel.")

            else:
                raise Http404("User does not exist.")

        elif 'demote_mod' in request.POST:
            
            if request.user.is_authenticated:
                channel_name = request.POST.get('channel_name')
                channel = Channel.objects.filter(channel_name=channel_name)
                
                if channel.exists():
                    channel = channel.get()

                    if is_owner(channel, request.user):
                    
                        moderators = json.loads(channel.moderators)
                        moderators = [u for u in moderators if not u == username]

                        channel.moderators = json.dumps(moderators)
                        channel.save()
                        
                    else:
                        raise Http404("Insufficient permissions.")
                
                else:
                    raise Http404("Couldn't find that channel.")

            else:
                raise Http404("User does not exist.")

        return HttpResponseRedirect(self.request.path_info)

class FavoritesView(ViewMixin, generic.DetailView):
    model = Channel
    template_name = 'forumapp/favorites.html'

    queryset = Channel.objects
    context_object_name = 'favorites_list'

    def get_object(self):
        if self.request.user.is_authenticated():
            settings = get_or_create_settings(self.request.user)
            return self.queryset.filter(channel_name__in=json.loads(settings.favorites))
        
        return self.queryset.none()

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('forumapp:channel'))

        if 'add_favorite' in request.POST:
            settings = get_or_create_settings(self.request.user)
            favs = json.loads(settings.favorites)
            channel_name = request.POST['channel_name']

            if not channel_name in favs:
                favs.append(channel_name)
                settings.favorites = json.dumps(favs)
                settings.save()
    
            else:
                messages.error(request, "Channel already in favorites")

        elif 'remove_favorite' in request.POST:
            settings = get_or_create_settings(self.request.user)
            favs = json.loads(settings.favorites)
            channel_name = request.POST['channel_name']
            
            if channel_name in favs:
                favs.remove(channel_name)
                settings.favorites = json.dumps(favs)
                settings.save()
            else:
                messages.error(request, "Channel not found in favorites")
        
        elif 'pin' in request.POST:
            channel_name = request.POST['channel_name']
            channel = self.queryset.filter(channel_name=channel_name)
            
            if channel.exists():
                channel = channel.get()
                
                # Require staff status to pin channels
                if request.user.is_staff:
                    channel.pin_date = timezone.now()
                    channel.save()

        elif 'unpin' in request.POST:
            channel_name = request.POST['channel_name']
            channel = self.queryset.filter(channel_name=channel_name)
            
            if channel.exists():
                channel = channel.get()
                
                # Require staff status to unpin channels
                if request.user.is_staff:
                    channel.pin_date = None
                    channel.save()
        
        return HttpResponseRedirect(self.request.path_info)
