# Generated by Django 5.1.3 on 2024-11-17 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='raw',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
