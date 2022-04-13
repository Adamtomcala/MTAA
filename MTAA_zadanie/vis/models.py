from django.db import models

# Create your models here.


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_type_id = models.ForeignKey('UserType', models.DO_NOTHING)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user_name = models.CharField(max_length=50)
    password = models.CharField(max_length=200)
    email = models.CharField(max_length=50, default="")
    id_school = models.CharField(max_length=50, default="")
    phone = models.CharField(max_length=50, default="")


class UserType(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=200)


class Message(models.Model):
    id = models.BigAutoField(primary_key=True)
    sender = models.ForeignKey('User', models.DO_NOTHING, related_name='sender_user')
    receiver = models.ForeignKey('User', models.DO_NOTHING, related_name='sender_receiver')
    name = models.CharField(max_length=200)
    text = models.CharField(max_length=200)
    created_at = models.DateTimeField()


class ClassroomUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING, related_name='user_classroom')
    classroom = models.ForeignKey('Classroom', models.DO_NOTHING, related_name='classroom_user')


class Classroom(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    lecture_name = models.CharField(max_length=50)


class Material(models.Model):
    id = models.BigAutoField(primary_key=True)
    classroom_id = models.ForeignKey('Classroom', models.DO_NOTHING, related_name='classroom_id')
    name = models.CharField(max_length=200)
    path = models.CharField(max_length=200)
    created_at = models.DateTimeField()
