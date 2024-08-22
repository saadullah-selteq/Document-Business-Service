# Generated by Django 5.0.8 on 2024-08-19 12:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='customer',
            fields=[
                ('ownerId', models.IntegerField(primary_key=True, serialize=False)),
                ('isAdmin', models.BooleanField(default=False)),
                ('totalStorage', models.CharField(blank=True, max_length=100)),
                ('remainingStorage', models.CharField(blank=True, max_length=100)),
                ('package', models.CharField(blank=True, max_length=100)),
                ('createdAt', models.DateTimeField(blank=True, null=True)),
                ('updatedAt', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='documentFolder',
            fields=[
                ('folderId', models.AutoField(primary_key=True, serialize=False)),
                ('folderName', models.CharField(blank=True, max_length=100)),
                ('folderPath', models.CharField(blank=True, max_length=100)),
                ('folderParentId', models.CharField(blank=True, max_length=100)),
                ('ownerId', models.CharField(blank=True, max_length=100)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now_add=True)),
                ('size', models.IntegerField(blank=True, default=0)),
                ('folderType', models.CharField(blank=True, max_length=100)),
                ('isPublic', models.BooleanField(default=False)),
                ('isLocked', models.BooleanField(default=False)),
                ('isDeleted', models.BooleanField(default=False)),
                ('permanantDelete', models.BooleanField(default=False)),
                ('permanantDeletedOn', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='documentFile',
            fields=[
                ('fileId', models.AutoField(primary_key=True, serialize=False)),
                ('fileName', models.CharField(blank=True, max_length=100)),
                ('filePath', models.CharField(blank=True, max_length=100)),
                ('ownerId', models.CharField(blank=True, max_length=100)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now_add=True)),
                ('size', models.CharField(blank=True, max_length=100)),
                ('type', models.CharField(blank=True, max_length=100)),
                ('isPublic', models.BooleanField(default=False)),
                ('isReadOnly', models.BooleanField(default=False)),
                ('fileUrl', models.CharField(blank=True, max_length=500)),
                ('isDeleted', models.BooleanField(default=False)),
                ('permanantDelete', models.BooleanField(default=False)),
                ('permanantDeletedOn', models.DateTimeField(blank=True, null=True)),
                ('folderId', models.ForeignKey(db_column='folderId', on_delete=django.db.models.deletion.CASCADE, to='documentService.documentfolder')),
            ],
        ),
    ]
