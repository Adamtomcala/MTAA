# Generated by Django 4.0.3 on 2022-03-24 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vis', '0004_alter_classroom_id_alter_classroomuser_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]