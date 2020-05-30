from django.contrib import admin
from .models import Channel, Thread, Comment
# Register your models here.

class ThreadInline(admin.TabularInline):
    model = Thread
    extra = 3

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 3

class ChannelAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['channel_name']}),
        ('Date Information', {'fields': ['pub_date']}),
        ('Owner'           , {'fields': ['owner']}),
    ]

    inlines = [ThreadInline]

    list_display = ('channel_name', 'owner', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['channel_name']

class ThreadAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,              {'fields': ['channel_name', 'thread_name', 'description']}),
        ('Date Information',{'fields': ['pub_date']}),
        ('Owner',           {'fields': ['owner']}),
    ]

    inlines = [CommentInline]

    list_display = ('channel_name', 'thread_name', 'description', 'owner', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['thread_name']

class CommentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['thread_id', 'text']}),
        ('Date Information', {'fields': ['pub_date']}),
        ('Owner'           , {'fields': ['owner']}),
    ]

    list_display = ('text', 'owner', 'pub_date', 'is_recent')
    list_filter = ['pub_date']
    search_fields = ['text']

admin.site.register(Channel, ChannelAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Comment, CommentAdmin)
