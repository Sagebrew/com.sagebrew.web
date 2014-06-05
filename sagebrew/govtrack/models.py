from django.db import models
from model_utils.models import TimeStampedModel

# Create your models here.

class Person(TimeStampedModel):
    bioguideid = models.CharField(max_length=8)
    birthday = models.DateField()
    cspanid = models.IntegerField()
    firstname = models.CharField(max_length=30)
    gender = models.CharField(max_length=15)
    gender_label = models.CharField(max_length=15)
    id = models.IntegerField(primary_key=True, unique=False)
    lastname = models.CharField(max_length=30)
    link = models.URLField()
    middlename = models.CharField(max_length=30)
    name = models.CharField(max_length=75)
    namemod = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100, null=True)
    osid = models.CharField(max_length=10)
    pvsid = models.IntegerField()
    sortname = models.CharField(max_length=100)
    twitterid = models.CharField(max_length=15, null=True)
    youtubeid = models.CharField(max_length=20, null=True)

class SRole(TimeStampedModel):
    congress_numbers = models.CommaSeparatedIntegerField(max_length=100)
    current = models.BooleanField(default=False)
    description = models.CharField(max_length=100)
    district = models.CharField(max_length=100, null=True)
    enddate = models.DateField()
    id = models.IntegerField(primary_key=True)
    leadership_title = models.CharField(max_length=100, null=True)
    party = models.CharField(max_length=100)
    person = models.ForeignKey(Person,blank=True, null=True)
    phone = models.CharField(max_length=12)
    role_type = models.CharField(max_length=30)
    role_type_label = models.CharField(max_length=30)
    senator_class = models.CharField(max_length=30, null=True)
    senator_class_label = models.CharField(max_length=30, null=True)
    senator_rank = models.CharField(max_length=30, null=True)
    senator_rank_label = models.CharField(max_length=30, null=True)
    startdate = models.DateField(null=True)
    state = models.CharField(max_length=2)
    title = models.CharField(max_length=10)
    title_long = models.CharField(max_length=30)
    website = models.URLField()

class GTBill(TimeStampedModel):
    bill_resolution_type = models.CharField(max_length=1000)
    bill_type = models.CharField(max_length=1000)
    bill_type_label = models.CharField(max_length=1000)
    congress = models.IntegerField()
    current_status = models.CharField(max_length=1000)
    current_status_date = models.DateField()
    current_status_description = models.CharField(max_length=1000)
    current_status_label = models.CharField(max_length=1000)
    display_number = models.CharField(max_length=1000)
    docs_house_gov_postdate = models.DateField(null=True)
    id = models.IntegerField(primary_key=True, unique = False)
    introduced_date = models.DateField()
    is_alive = models.BooleanField()
    is_current = models.BooleanField()
    link = models.URLField()
    major_actions = models.CharField(max_length=1000,null=True)
    noun = models.CharField(max_length=1000)
    number = models.IntegerField()
    senate_floor_schedule_postdate = models.DateField(null=True)
    sliplawnum = models.IntegerField(null=True)
    sliplawpubpriv = models.IntegerField(null=True)
    source = models.CharField(max_length=300)
    source_link = models.URLField(null=True)
    sponsor = models.IntegerField()
    sponsor_role = models.IntegerField()
    thomas_link = models.URLField()
    title = models.CharField(max_length=1000)
    title_without_number = models.CharField(max_length=1000)
    titles = models.CharField(max_length=1000)
















