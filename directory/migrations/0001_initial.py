# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import directory.phonenumber
import directory.twitter
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text=b'The full name of the city (e.g., New York City).', max_length=100)),
                ('short_name', models.CharField(help_text=b'The short/abbreviated name of the city (e.g., NYC).', max_length=20, blank=True)),
                ('slug', models.SlugField(help_text=b'A short identifier for the city, used in URLs and such. Only letters, numbers, underscores, and hyphens are allowed.', unique=True)),
                ('site', models.OneToOneField(null=True, blank=True, to='sites.Site', help_text=b"The site associated with this city. If blank, this city's directory will only be accessible on multi-city sites.")),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'cities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContentChannel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('category', models.CharField(help_text=b'The type of the content channel', max_length=15, choices=[(b'facebook', b'Facebook'), (b'youtube', b'YouTube'), (b'vimeo', b'Vimeo'), (b'flickr', b'Flickr'), (b'tumblr', b'Tumblr'), (b'pinterest', b'Pinterest'), (b'github', b'GitHub'), (b'instagram', b'Instagram'), (b'other', b'Other')])),
                ('name', models.CharField(help_text=b'The name of the content channel.', max_length=100, blank=True)),
                ('url', models.URLField(help_text=b'The URL of the content channel.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Expertise',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('category', models.CharField(help_text=b'The type of the expertise', max_length=25, choices=[(b'youth', b'Youth'), (b'partnerships', b'Collaboration and Partnerships'), (b'rfp', b'RFP'), (b'leveragingresources', b'Leveraging Resources'), (b'volunteers', b'Mentors and Volunteers'), (b'sharingoutcomes', b'Sharing Outcomes'), (b'events', b'Activities and Events'), (b'programdesign', b'Program Design and Facilitation'), (b'badges', b'Badges'), (b'innovation', b'Innovation Design Strategies'), (b'leveraginghive', b'Leveraging Hive'), (b'curriculum', b'Curriculum Development'), (b'assessment', b'Assessment and Evaluative Approaches'), (b'technology', b'Technological Solutions and Possibilities'), (b'other', b'Other')])),
                ('details', models.CharField(help_text=b'Details about the expertise', max_length=255, blank=True)),
                ('user', models.ForeignKey(related_name='skills', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImportedUserInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('was_sent_email', models.BooleanField(default=False, help_text=b'Whether the imported user has been sent an email informing them of their new account.')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(help_text=b"The person's title at their organization.", max_length=100, blank=True)),
                ('bio', models.TextField(help_text=b"The person's biography. Markdown and basic HTML tags are allowed.", blank=True)),
                ('twitter_name', models.CharField(blank=True, help_text=b'The twitter account for the person.', max_length=15, validators=[directory.twitter.validate_twitter_name])),
                ('phone_number', models.CharField(blank=True, help_text=b"The person's phone number.", max_length=12, validators=[directory.phonenumber.validate_phone_number])),
                ('receives_minigroup_digest', models.BooleanField(default=False, help_text=b'Whether the person is sent a daily digest of Minigroup activity.')),
                ('is_listed', models.BooleanField(default=True, help_text=b'Whether the person is listed under their organization in the Hive directory.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MembershipRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'The name of the role.', max_length=50)),
                ('description', models.TextField(help_text=b'Description of the role.')),
                ('city', models.ForeignKey(help_text=b'The Hive city that the role pertains to.', to='directory.City')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text=b'The full name of the organization.', max_length=100)),
                ('slug', models.SlugField(help_text=b'A short identifier for the organization, used in URLs and such. Only letters, numbers, underscores, and hyphens are allowed.', unique=True)),
                ('website', models.URLField(help_text=b"The URL of the organization's primary website.")),
                ('email_domain', models.CharField(help_text=b'The domain which members of this organization have email addresses at.', max_length=50, blank=True)),
                ('address', models.TextField(help_text=b"The full address of the organization's main office.", blank=True)),
                ('twitter_name', models.CharField(blank=True, help_text=b'The twitter account for the organization.', max_length=15, validators=[directory.twitter.validate_twitter_name])),
                ('hive_member_since', models.DateField(help_text=b'The date the organization joined the Hive network. Only the month and year will be used.', null=True, blank=True)),
                ('mission', models.TextField(help_text=b"The organization's mission and philosophy. Markdown and basic HTML tags are allowed.", blank=True)),
                ('min_youth_audience_age', models.SmallIntegerField(default=0, help_text=b"Minimum age of youth, in years, that the organization's programs target.", validators=[django.core.validators.MinValueValidator(0)])),
                ('max_youth_audience_age', models.SmallIntegerField(default=18, help_text=b"Maximum age of youth, in years, that the organization's programs target.", validators=[django.core.validators.MinValueValidator(0)])),
                ('is_active', models.BooleanField(default=True, help_text=b'Designates whether this organization should be treated as active. Unselect this instead of deleting organizations.')),
                ('city', models.ForeignKey(help_text=b'The city to which the organization belongs.', to='directory.City')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganizationMembershipType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'The name of the organization membership type.', max_length=50)),
                ('description', models.TextField(help_text=b'Description of the organization membership type.')),
                ('city', models.ForeignKey(help_text=b'The Hive city that the membership type pertains to.', to='directory.City')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='organization',
            name='membership_types',
            field=models.ManyToManyField(related_name='orgs', to='directory.OrganizationMembershipType', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='membership',
            name='organization',
            field=models.ForeignKey(related_name='memberships', blank=True, to='directory.Organization', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='membership',
            name='roles',
            field=models.ManyToManyField(to='directory.MembershipRole', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contentchannel',
            name='organization',
            field=models.ForeignKey(related_name='content_channels', to='directory.Organization'),
            preserve_default=True,
        ),
    ]
