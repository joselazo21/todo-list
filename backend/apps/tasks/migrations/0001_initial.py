# Generated by Django 5.2.1 on 2025-06-06 06:05

import django.core.validators
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TaskModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Task title (minimum 3 characters)', max_length=200, validators=[django.core.validators.MinLengthValidator(3)])),
                ('description', models.TextField(blank=True, help_text='Detailed task description')),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', help_text='Task priority level', max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', help_text='Task status', max_length=15)),
                ('due_date', models.DateTimeField(blank=True, help_text='Task due date and time', null=True)),
                ('completed_at', models.DateTimeField(blank=True, help_text='When the task was completed', null=True)),
                ('user_id', models.UUIDField(help_text='Task owner ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'db_table': 'tasks_task',
                'ordering': ['-priority', 'due_date', '-created_at'],
                'indexes': [models.Index(fields=['user_id', 'status'], name='tasks_task_user_id_c0fce1_idx'), models.Index(fields=['due_date'], name='tasks_task_due_dat_bce847_idx'), models.Index(fields=['priority'], name='tasks_task_priorit_a900d4_idx'), models.Index(fields=['created_at'], name='tasks_task_created_be1ba2_idx'), models.Index(fields=['status'], name='tasks_task_status_4a0a95_idx')],
            },
        ),
    ]
