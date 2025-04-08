from django.contrib import admin
from .models import Flashcard


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('id', 'front_text_preview', 'back_text_preview', 'num_revisions', 'created_at', 'updated_at')
    list_filter = ('num_revisions', 'created_at', 'updated_at')
    search_fields = ('front_text', 'back_text')
    ordering = ('-updated_at',)

    def front_text_preview(self, obj):
        return obj.front_text[:50] + "..." if len(obj.front_text) > 50 else obj.front_text

    def back_text_preview(self, obj):
        return obj.back_text[:50] + "..." if len(obj.back_text) > 50 else obj.back_text

    front_text_preview.short_description = 'Front Text'
    back_text_preview.short_description = 'Back Text'