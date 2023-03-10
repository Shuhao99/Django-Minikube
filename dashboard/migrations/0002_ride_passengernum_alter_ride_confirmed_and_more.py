# Generated by Django 4.1.5 on 2023-01-31 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ride',
            name='passengerNum',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='ride',
            name='confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='ride',
            name='if_share',
            field=models.BooleanField(default=False, help_text='Muted by default'),
        ),
        migrations.AlterField(
            model_name='ride',
            name='shared_by_user',
            field=models.ManyToManyField(blank=True, default=None, to='dashboard.group'),
        ),
    ]
