from django.contrib import admin
from .models import Post, Comment, Memo

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Memo)
