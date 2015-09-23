# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_auto_20150911_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='lambdaapplication',
            name='failure_message',
            field=models.TextField(default=b'', help_text=b'Error message regarding this application.'),
        ),
        migrations.AddField(
            model_name='lambdaapplication',
            name='name',
            field=models.CharField(default=b'', max_length=100),
        ),
        migrations.AddField(
            model_name='lambdaapplication',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, to='backend.User', null=True),
        ),
        migrations.AddField(
            model_name='lambdaapplication',
            name='status',
            field=models.CharField(default=b'1', help_text=b'The status of this application.', max_length=10, choices=[(b'0', b'UPLOADED'), (b'1', b'UPLOADING'), (b'2', b'FAILED')]),
        ),
        migrations.AddField(
            model_name='lambdaapplication',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, help_text=b'Application uuid.', unique=True, verbose_name=b'uuid'),
        ),
    ]
