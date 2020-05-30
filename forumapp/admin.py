from django.contrib import admin
from .models import Channel, Thread, Comment
# Register your models here.

class ThreadInline(admin.TabularInline):
    model = Thread
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

admin.site.register(Channel, ChannelAdmin)
#admin.site.register(Choice)
