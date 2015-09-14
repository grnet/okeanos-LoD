# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_auto_20150909_2239'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LambdaInstanceProjectConnection',
            new_name='LambdaInstanceApplicationConnection',
        ),
    ]
