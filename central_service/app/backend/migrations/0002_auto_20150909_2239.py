# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lambdainstance',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text=b'Unique key assigned to every instance.', unique=True, verbose_name=b'Instance UUID'),
        ),
    ]
