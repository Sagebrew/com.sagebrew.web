from django.db import models
from model_utils.models import TimeStampedModel
from django.forms import ModelForm

# Create your models here.

class Person(TimeStampedModel):
    bioguideid = models.CharField(max_length=8)
    birthday = models.DateField()
    cspanid = models.IntegerField()
    firstname = models.CharField(max_length=30)
    gender = models.CharField(max_length=15)
    gender_label = models.CharField(max_length=15)
    id = models.IntegerField(primary_key=True)
    lastname = models.CharField(max_length=30)
    link = models.URLField()
    middlename = models.CharField(max_length=30)
    name = models.CharField(max_length=75)
    namemod = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100)
    osid = models.CharField(max_length=10)
    pvsid = models.IntegerField()
    sortname = models.CharField(max_length=100)
    twitterid = models.CharField(max_length=15)
    youtubeid = models.CharField(max_length=20)

class Role(TimeStampedModel):
    congress_numbers = models.CommaSeparatedIntegerField()
    current = models.BinaryField()
    description = models.CharField(max_length=100)
    district = models.CharField(max_length=100,null=True)
    enddate = models.DateField()
    id = models.IntegerField(primary_key=True)
    leadership_title = models.CharField(max_length=100,null=True)
    party = models.CharField(max_length=100)
    person = models.ForeignKey(Person)
    phone = models.CharField(max_length=12)
    role_type = models.CharField(max_length=30)
    role_type_label = models.CharField(max_length=30)
    senator_class = models.CharField(max_length=30)
    senator_class_label = models.CharField(max_length=30)
    startdate = models.DateField()
    state = models.CharField(max_length=2)
    title = models.CharField(max_length=10)
    title_long = models.CharField(max_length=30)
    website = models.URLField()

class Bill(models.Model):
    asd = models.CharField(max_length=100)













