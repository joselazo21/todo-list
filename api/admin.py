from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import User, Task, TaskPriority


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Enhanced User admin interface"""
    list_display = ['name', 'email', 'is_active', 'tasks_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'tasks_count']
    ordering = ['name']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'tasks_count'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with task count"""
        return super().get_queryset(request).annotate(
            task_count=Count('tasks')
        )

    def tasks_count(self, obj):
        """Display task count"""
        return obj.task_count
    tasks_count.short_description = 'Tasks'
    tasks_count.admin_order_field = 'task_count'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Enhanced Task admin interface"""
    list_display = [
        'title', 'user_name', 'priority_badge', 'completed_badge', 
        'due_date', 'is_overdue_badge', 'created_at'
    ]
    list_filter = [
        'completed', 'priority', 'created_at', 'due_date',
        ('user', admin.RelatedOnlyFieldListFilter),
    ]
    search_fields = ['title', 'description', 'user__name', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'is_overdue']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'user')
        }),
        ('Status & Priority', {
            'fields': ('completed', 'priority', 'due_date', 'completed_at')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'is_overdue'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_completed', 'mark_pending', 'set_high_priority']

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user')

    def user_name(self, obj):
        """Display user name"""
        return obj.user.name
    user_name.short_description = 'User'
    user_name.admin_order_field = 'user__name'

    def priority_badge(self, obj):
        """Display priority with color coding"""
        colors = {
            TaskPriority.LOW: '#28a745',
            TaskPriority.MEDIUM: '#ffc107', 
            TaskPriority.HIGH: '#fd7e14',
            TaskPriority.URGENT: '#dc3545',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    priority_badge.admin_order_field = 'priority'

    def completed_badge(self, obj):
        """Display completion status with icons"""
        if obj.completed:
            return format_html(
                '<span style="color: green;">✓ Completed</span>'
            )
        return format_html(
            '<span style="color: orange;">○ Pending</span>'
        )
    completed_badge.short_description = 'Status'
    completed_badge.admin_order_field = 'completed'

    def is_overdue_badge(self, obj):
        """Display overdue status"""
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ OVERDUE</span>'
            )
        return format_html('<span style="color: green;">✓ On time</span>')
    is_overdue_badge.short_description = 'Due Status'

    def mark_completed(self, request, queryset):
        """Mark selected tasks as completed"""
        from django.utils import timezone
        updated = queryset.filter(completed=False).update(
            completed=True,
            completed_at=timezone.now()
        )
        self.message_user(request, f'{updated} tasks marked as completed.')
    mark_completed.short_description = "Mark selected tasks as completed"

    def mark_pending(self, request, queryset):
        """Mark selected tasks as pending"""
        updated = queryset.filter(completed=True).update(
            completed=False,
            completed_at=None
        )
        self.message_user(request, f'{updated} tasks marked as pending.')
    mark_pending.short_description = "Mark selected tasks as pending"

    def set_high_priority(self, request, queryset):
        """Set selected tasks to high priority"""
        updated = queryset.update(priority=TaskPriority.HIGH)
        self.message_user(request, f'{updated} tasks set to high priority.')
    set_high_priority.short_description = "Set selected tasks to high priority"


# Customize admin site
admin.site.site_header = "Todo List Administration"
admin.site.site_title = "Todo List Admin"
admin.site.index_title = "Welcome to Todo List Administration"
