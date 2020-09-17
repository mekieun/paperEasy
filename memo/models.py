from django.db import models
from django.contrib.auth.models import User


class Bookmark(models.Model):
    site_name = models.CharField(max_length=500)
    url = models.URLField('Site URL')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return "내용: " + self.site_name + ", 주소: " + self.url
        # 객체를 출력할 때 나타나는 값
