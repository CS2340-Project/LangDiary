from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Goal


# Customize the User admin display
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)


class GoalAdmin(admin.ModelAdmin):
    list_display = (
    'title', 'user', 'target_value', 'current_value', 'unit', 'deadline', 'progress_percentage', 'is_completed')
    list_filter = ('unit', 'created_at', 'deadline')
    search_fields = ('title', 'description', 'user__username')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    readonly_fields = ('progress_percentage', 'is_completed')

    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description')
        }),
        ('Progress', {
            'fields': ('target_value', 'current_value', 'unit', 'progress_percentage', 'is_completed')
        }),
        ('Timeline', {
            'fields': ('deadline', 'created_at')
        }),
    )



# Unregister the default User admin and register our customized version
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Goal, GoalAdmin)
