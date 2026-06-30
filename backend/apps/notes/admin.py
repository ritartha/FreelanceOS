from django.contrib import admin

from apps.notes.models import Note, NoteAttachment

admin.site.register(Note)
admin.site.register(NoteAttachment)
