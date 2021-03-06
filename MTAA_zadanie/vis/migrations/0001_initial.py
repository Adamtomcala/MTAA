# Generated by Django 4.0.2 on 2022-03-22 11:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('lecture_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('user_name', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('user_type_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='vis.usertype')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('text', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField()),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='sender_receiver', to='vis.user')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='sender_user', to='vis.user')),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('path', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField()),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='teacher_classroom', to='vis.classroom')),
            ],
        ),
        migrations.CreateModel(
            name='ClassroomUser',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='classroom_user', to='vis.classroom')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_classroom', to='vis.user')),
            ],
        ),
        migrations.AddField(
            model_name='classroom',
            name='material',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='vis.material'),
        ),
        migrations.AddField(
            model_name='classroom',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='classroomuser', to='vis.classroomuser'),
        ),
    ]
