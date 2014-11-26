from django.db import models

from directory.models import City

class CityBlog(models.Model):
    '''
    Represents a WordPress blog for a Hive city.
    '''

    city = models.OneToOneField(
        City,
        help_text="City the blog is for. Must be a WordPress blog.",
    )
    url = models.URLField(
        help_text="URL to the WordPress blog's front page."
    )

    def __unicode__(self):
        return u'%s blog' % self.city.name
