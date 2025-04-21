from django.contrib import admin
from .models import LanguageVideo

@admin.register(LanguageVideo)
class LanguageVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'level', 'video_type', 'is_watched', 'is_favorite', 'created_at')
    list_filter = ('language', 'level', 'video_type', 'is_watched', 'is_favorite')
    search_fields = ('title', 'description', 'notes')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'youtube_id', 'description', 'notes')
        }),
        ('Classification', {
            'fields': ('language', 'level', 'video_type', 'duration')
        }),
        ('Status', {
            'fields': ('is_watched', 'is_favorite', 'created_at')
        }),
    )