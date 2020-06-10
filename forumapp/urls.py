"""django_forum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views

app_name = 'forumapp'
urlpatterns = [
    url(r'^settings/$', views.UserSettingsView.as_view(), name='settings'),
    url(r'^settings/(?P<channel>[-\w]+)/$', views.ChannelSettingsView.as_view(), name='channel_settings'),
    url(r'^favorites/$', views.FavoritesView.as_view(), name='favorites'),
    url(r'^user/(?P<username>[-\w]+)/$', views.UserView.as_view(), name='user'),
    url(r'^(?P<channel>[-\w]+)/(?P<thread>[0-9]+)/$', views.CommentView.as_view(), name='comment'),
    url(r'^(?P<channel>[-\w]+)/$', views.ThreadView.as_view(), name='thread'),
    url(r'^$', views.ChannelView.as_view(), name='channel'),
]
