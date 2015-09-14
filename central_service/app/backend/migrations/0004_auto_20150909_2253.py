# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_auto_20150909_2249'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lambdainstanceapplicationconnection',
            old_name='project',
            new_name='application',
        ),
    ]
