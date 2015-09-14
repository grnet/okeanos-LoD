# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_auto_20150911_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lambdainstance',
            name='owner',
            field=models.ForeignKey(related_name='lambda_instances', to='backend.User'),
        ),
    ]
