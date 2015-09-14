# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_auto_20150909_2253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lambdainstance',
            name='owner',
            field=models.OneToOneField(related_name='lambda_instance', to='backend.User'),
        ),
    ]
