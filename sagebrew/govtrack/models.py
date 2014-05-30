from django.db import models

# Create your models here.
# For use with legislators-current.csv
# Everything is in the order with the document

class Congressman(models.Model):
    congress_numbers= models.IntegerField()
    last_name= models.CharField(max_length=100)
    first_name= models.CharField(max_length=100)
    birthday= models.DateField()
    gender= models.CharField(max_length=30)
    type= models.CharField(max_length=30)
    state= models.CharField(max_length=2)
    party= models.CharField(max_length=30)
    url= models.URLField()
    address= models.CharField(max_length=100)
    phone= models.IntegerField()
    contact_form= models.URLField()
    rss_url= models.URLField()
    twitter= models.CharField(max_length=100)
    facebook= models.CharField(max_length=100)
    facebook_id= models.IntegerField()
    youtube= models.CharField(max_length=100)
    youtube_id= models.CharField(max_length=100)
    bioguide_id= models.CharField(max_length=10)
    thomas_id= models.IntegerField()
    opensecrets_id= models.CharField(max_length=10)
    lis_id= models.CharField(max_length=5)
    cspan_id= models.IntegerField()
    govtrack_id= models.IntegerField()
    votesmart_id= models.IntegerField()
    ballotpedia_id= models.CharField(max_length=100)
    washington_post_id= models.CharField(max_length=100)
    icpsr_id= models.IntegerField()
    wikipedia_id= models.CharField(max_length=100)

class Bill(models.Model):
    asd = models.CharField(max_length=100)













