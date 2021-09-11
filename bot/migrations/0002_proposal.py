# Generated by Django 3.2.6 on 2021-09-11 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref_id', models.CharField(max_length=2000, unique=True)),
                ('proposal_title', models.CharField(max_length=2000)),
                ('protocol', models.CharField(max_length=2000)),
                ('current_state', models.CharField(max_length=256)),
                ('results', models.JSONField()),
                ('total_votes', models.IntegerField()),
                ('remind_in_seconds', models.IntegerField()),
            ],
        ),
    ]