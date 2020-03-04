# Generated by Django 3.0.3 on 2020-03-04 01:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0003_rankta'),
    ]

    operations = [
        migrations.CreateModel(
            name='RankCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(default=0)),
                ('TA', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.TA')),
                ('curriculum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.Course')),
            ],
        ),
    ]