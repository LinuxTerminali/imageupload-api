from django.db import models
from django.contrib.auth.models import User
from .utils import manipulate


def user_directory_path(instance, filename):
    user_name = manipulate.encrypt_username(
        instance.owner.username, instance.owner.id)
    return 'cloud_{0}/{1}'.format(user_name, filename)


class ImageUpload(models.Model):
    file = models.ImageField(blank=False, null=False,
                             upload_to=user_directory_path)
    title = models.CharField(max_length=100, help_text=("Name for the uploade image"))
    description = models.CharField(max_length=300, default='')
    timestamp = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, default=1, null=False)
    shared = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return self.file
