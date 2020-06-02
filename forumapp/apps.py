from django.apps import AppConfig


class ForumappConfig(AppConfig):
    name = 'forumapp'

    def ready(self):
        import forumapp.signals
