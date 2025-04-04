# Generated by Django 5.1.7 on 2025-03-07 11:19

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(help_text='email must be unique', max_length=254, unique=True, verbose_name='email address')),
                ('username', models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator(message='Username must be alphanumeric or should contain underscore', regex='^[a-zA-Z0-9_]+$')], verbose_name='User_name')),
                ('fullname', models.CharField(help_text='Enter your full name as appeared on your official document', max_length=250, verbose_name='user full name')),
                ('role', models.CharField(choices=[('parent', 'Parent'), ('health_worker', 'Health Worker')], max_length=20, verbose_name='user role')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user account should be treated as active', verbose_name='active')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether this user account should be treated as staff', verbose_name='staff')),
                ('deleated_at', models.DateTimeField(blank=True, help_text='Time stamp for the soft deletion', null=True, verbose_name='deleated at')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('language_preferences', models.CharField(choices=[('eng', 'English'), ('swa', 'swahili'), ('fr', 'French')], default='eng', max_length=20, verbose_name='language preference')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'ordering': ['-date_joined'],
            },
        ),
        migrations.CreateModel(
            name='HealthWorkerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('professional_id', models.CharField(max_length=50, verbose_name='Professional_id')),
                ('health_facility', models.CharField(max_length=100, verbose_name='Health facility')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Health worker Profile',
            },
        ),
        migrations.CreateModel(
            name='ParentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField(max_length=100, verbose_name='parent address')),
                ('phone_number', models.CharField(max_length=10, verbose_name='phone number')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Parent Profile',
            },
        ),
    ]
