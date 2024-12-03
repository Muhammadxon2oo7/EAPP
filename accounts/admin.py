from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'tin', 'is_physic', 'is_staff', 'is_superuser', 'id', 'is_online')
    search_fields = ('email', 'tin')
    list_filter = ('is_staff', 'is_superuser', 'is_physic')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('photo', 'tin', 'is_physic')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)





# from django.contrib import admin
#
# from .models import User
#
#
# admin.site.register(User)
