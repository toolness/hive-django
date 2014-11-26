# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0002_city_hive_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='CityBlog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(help_text=b"URL to the blog's front page.")),
                ('city', models.OneToOneField(to='directory.City', help_text=b'City the blog is for. Must be a WordPress blog.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
