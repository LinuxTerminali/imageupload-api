# Generated by Django 2.1 on 2018-08-21 05:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import imagecloud.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(upload_to=imagecloud.models.user_directory_path)),
                ('title', models.CharField(help_text='Name for the uploade image', max_length=100)),
                ('description', models.CharField(default='', max_length=300)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('shared', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
