# Generated by Django 2.2.3 on 2019-07-12 09:36

import builtins
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_auto_20190712_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.ForeignKey(on_delete=builtins.id, to='store.Author'),
        ),
        migrations.AlterField(
            model_name='review',
            name='book',
            field=models.ForeignKey(on_delete=builtins.id, to='store.Book'),
        ),
        migrations.AlterField(
            model_name='review',
            name='user',
            field=models.ForeignKey(on_delete=builtins.id, to=settings.AUTH_USER_MODEL),
        ),
    ]
