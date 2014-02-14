from django.db import models

# Create your models here.

class Organization(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField()
    address = models.TextField()
    twitter_name = models.CharField(max_length=15)
    hive_member_since = models.DateField()
    mission = models.TextField()

    # TODO: How to represent youth audience?

    # TODO: How to represent different content channels? e.g.,
    # youtube, blog, flickr, instagram, etc?
