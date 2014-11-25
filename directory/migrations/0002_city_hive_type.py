# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='hive_type',
            field=models.CharField(default=b'emerging', help_text=b'The type of Hive in this city.', max_length=25, choices=[(b'emerging', b'Emerging'), (b'community', b'Community'), (b'network', b'Network')]),
            preserve_default=True,
        ),
    ]
