from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import User,UserAdmin
from apply.models import *

UserAdmin.list_display = ('username','email','first_name','last_name','is_staff','date_joined')

admin.site.unregister(User)
admin.site.register(User,UserAdmin)
admin.site.register(ProfileStatus)
admin.site.register(ProfileHelpText)
admin.site.register(AttachmentType)
admin.site.register(Contact)
admin.site.register(ContactEmail)
admin.site.register(LogEntry)
