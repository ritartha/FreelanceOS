from django.contrib import admin

from apps.files.models import FileAttachment, FileTag, FileVersion, Folder

admin.site.register(FileAttachment)
admin.site.register(Folder)
admin.site.register(FileTag)
admin.site.register(FileVersion)
