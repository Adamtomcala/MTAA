from django.db import models

# Create your models here.


class User(models.Model):
    id = models.AutoField(primary_key=True)
    user_type_id = models.ForeignKey('UserType', models.DO_NOTHING)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)


class UserType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=200)


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey('User', models.DO_NOTHING)
    receiver = models.ForeignKey('User', models.DO_NOTHING)
    name = models.CharField(max_length=200)
    text = models.CharField(max_length=200)
    created_at = models.DateTimeField()


class ClassroomUser(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('User', models.DO_NOTHING)
    classroom_id = models.ForeignKey('Classroom', models.DO_NOTHING)


class Classroom(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('ClassroomUser', models.DO_NOTHING)
    material_id = models.ForeignKey('Material', models.DO_NOTHING)
    name = models.CharField(max_length=50)
    lecture_name = models.CharField(max_length=50)


class Material(models.Model):
    id = models.AutoField(primary_key=True)
    teacher_id = models.ForeignKey('Classroom', models.DO_NOTHING)
    name = models.CharField(max_length=200)
    path = models.CharField(max_length=200)
    created_at = models.DateTimeField()
