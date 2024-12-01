from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class UserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'username','role', 'is_staff')
    fieldsets = (
        ('Personal info', {'fields': ('username', 'password', 'role', 'is_staff')}),
    )

admin.site.register(User, UserAdmin)
