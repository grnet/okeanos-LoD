# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LambdaApplication',
            fields=[
                ('id', models.AutoField(help_text=b'Auto-increment instance id.', serialize=False,
                                        verbose_name=b'Lambda Application ID', primary_key=True)),
                ('uuid',
                 models.UUIDField(default=uuid.uuid4, help_text=b'Application uuid.', unique=True,
                                  verbose_name=b'uuid')),
                ('name', models.CharField(default=b'', max_length=100)),
                ('description', models.TextField(
                    help_text=b'The description of the lambda application running on an instance',
                    blank=b'True')),
                ('status',
                 models.CharField(default=b'1', help_text=b'The status of this application.',
                                  max_length=10, choices=[(b'0', b'UPLOADED'), (b'1', b'UPLOADING'),
                                                          (b'2', b'FAILED')])),
                ('failure_message', models.TextField(default=b'',
                                                     help_text=b'Error message regarding this '
                                                               b'application.')),
            ],
        ),
        migrations.CreateModel(
            name='LambdaInstance',
            fields=[
                ('id', models.AutoField(help_text=b'Auto-increment instance id.', serialize=False,
                                        verbose_name=b'Instance ID', primary_key=True)),
                ('instance_info',
                 models.TextField(default=b'{}', help_text=b'Instance information in json format.',
                                  verbose_name=b'Instance info')),
                ('name', models.CharField(default=b'Lambda Instance',
                                          help_text=b'A name given to the instance.',
                                          max_length=100)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False,
                                          help_text=b'Unique key assigned to every instance.',
                                          unique=True, verbose_name=b'Instance UUID')),
                ('failure_message', models.TextField(default=b'',
                                                     help_text=b'Error message regarding this '
                                                               b'lambda instance')),
                ('status', models.CharField(default=b'2', help_text=b'The status of this instance.',
                                            max_length=10,
                                            choices=[(b'0', b'STARTED'), (b'1', b'STOPPED'),
                                                     (b'2', b'PENDING'), (b'3', b'STARTING'),
                                                     (b'4', b'STOPPING'), (b'5', b'DESTROYING'),
                                                     (b'6', b'DESTROYED'), (b'7', b'SCALING_UP'),
                                                     (b'8', b'SCALING_DOWN'), (b'9', b'FAILED'),
                                                     (b'10', b'CLUSTER_CREATED'),
                                                     (b'11', b'CLUSTER_FAILED'),
                                                     (b'12', b'INIT_DONE'), (b'13', b'INIT_FAILED'),
                                                     (b'14', b'COMMONS_INSTALLED'),
                                                     (b'15', b'COMMONS_FAILED'),
                                                     (b'16', b'HADOOP_INSTALLED'),
                                                     (b'17', b'HADOOP_FAILED'),
                                                     (b'18', b'KAFKA_INSTALLED'),
                                                     (b'19', b'KAFKA_FAILED'),
                                                     (b'20', b'FLINK_INSTALLED'),
                                                     (b'21', b'FLINK_FAILED')])),
            ],
            options={
                'verbose_name': 'Lambda Instance',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('key', models.CharField(max_length=100, null=True)),
                ('creation_date', models.DateTimeField(verbose_name=b'Creation Date')),
            ],
            options={
                'verbose_name': 'Token',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name=b'id', primary_key=True)),
                ('uuid',
                 models.CharField(default=b'', help_text=b'Unique user id assigned by Astakos',
                                  unique=True, max_length=255, verbose_name=b'uuid')),
            ],
            options={
                'verbose_name': 'User',
            },
        ),
        migrations.AddField(
            model_name='token',
            name='user',
            field=models.OneToOneField(related_name='kamaki_token', to='backend.User'),
        ),
        migrations.AddField(
            model_name='lambdainstance',
            name='owner',
            field=models.ForeignKey(related_name='lambda_instances', to='backend.User'),
        ),
        migrations.AddField(
            model_name='lambdaapplication',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None,
                                    to='backend.User', null=True),
        ),
    ]
