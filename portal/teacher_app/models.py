from django.db import models


# Create your models here.
class Subject(models.Model):
    display_name = models.CharField(max_length=100, unique=True, verbose_name="Subject")


class Teacher(models.Model):
    first_name = models.CharField(max_length=200, null=False, blank=False, verbose_name="First Name")
    last_name = models.CharField(max_length=200, null=False, blank=False, verbose_name="Last Name")
    profile_picture = models.ImageField(upload_to='teachers/profile/', blank=True)
    email_address = models.CharField(max_length=255,  null=False, blank=False, unique=True, verbose_name="Email Address")
    phone_number = models.CharField(max_length=100, verbose_name="Phone Number")
    room_number = models.CharField(max_length=100, verbose_name="Room Number")

    subjects_taught = models.ManyToManyField(Subject)
