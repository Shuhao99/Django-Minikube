# Generated by Django 4.1.5 on 2023-01-30 07:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groupNum', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicleType', models.IntegerField(choices=[(0, 'Sedan'), (1, 'SUV'), (2, 'Coupe'), (3, 'Hatchback'), (4, 'Mini van')], help_text='-Sedan: 4 door trunks, capacity: 4 <br/>        -SUV: Sport-Utility Vehicle, capacity: 5 <br/>        -Coupe: 2 door trunks, capacity: 2 <br/>        -Hatchback: Compact sedan, capacity: 4 <br/>        -Minivan: Trunks with large cargo area, capacity: 7 <br/>        * The capacity includes driver. ')),
                ('plateNumber', models.CharField(max_length=20)),
                ('owner', models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='vehicle', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ride',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicleType', models.IntegerField(choices=[(0, 'Sedan'), (1, 'SUV'), (2, 'Coupe'), (3, 'Hatchback'), (4, 'Mini van')], help_text='-Sedan: 4 door trunks, capacity: 4 <br/>        -SUV: Sport-Utility Vehicle, capacity: 5 <br/>        -Coupe: 2 door trunks, capacity: 2 <br/>        -Hatchback: Compact sedan, capacity: 4 <br/>        -Minivan: Trunks with large cargo area, capacity: 7 <br/>        * The capacity includes driver. ')),
                ('dest', models.TextField(max_length=100)),
                ('arrive_time', models.DateTimeField()),
                ('if_share', models.BooleanField()),
                ('completed', models.BooleanField(default=False)),
                ('confirmed', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('shared_by_user', models.ManyToManyField(to='dashboard.group')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('dob', models.DateTimeField()),
                ('gender', models.IntegerField(choices=[(0, 'female'), (1, 'male'), (2, 'prefer not to tell')])),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
