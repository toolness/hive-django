[![Build Status](https://secure.travis-ci.org/toolness/hive-django.png?branch=master)](http://travis-ci.org/toolness/hive-django)

## Requirements

* Python 2.7
* [pip and virtualenv](http://stackoverflow.com/q/4324558)

## Quick Start

```
virtualenv venv

# On Windows, replace the following line with 'venv\Scripts\activate'.
source venv/bin/activate

pip install -r requirements.minimal.txt
python manage.py syncdb --noinput
python manage.py initgroups
python manage.py seeddata
python manage.py runserver
```

At this point, you can visit http://localhost:8000/admin and log in as
user **admin** with password **test**.

## Environment Variables

Unlike traditional Django settings, we use environment variables
for configuration to be compliant with [twelve-factor][] apps.

**Note:** When an environment variable is described as representing a
boolean value, if the variable exists with *any* value (even the empty
string), the boolean is true; otherwise, it's false.

**Note:** When running `manage.py`, the following environment
variables are given default values: `SECRET_KEY`, `PORT`, `ORIGIN`,
`EMAIL_BACKEND_URL`. Also, `DEBUG` is enabled.

* `SECRET_KEY` is a large random value.
* `DEBUG` is a boolean value that indicates whether debugging is enabled
  (this should always be false in production).
* `PORT` is the port that the server binds to.
* `ORIGIN` is the origin of the server, as it appears
  to users. If `DEBUG` is enabled, this defaults to
  `http://localhost:PORT`. Otherwise, it must be defined.
* `DATABASE_URL` is the URL for the database. Defaults to a `sqlite://`
  URL pointing to `db.sqlite3` at the root of the repository. If this
  value is the name of another (all-caps) environment variable, e.g.
  `HEROKU_POSTGRESQL_AMBER_URL`, that variable's value will be used
  as the database URL.
* `EMAIL_BACKEND_URL` is a URL representing the email backend to use.
  Examples include `console:`, `smtp://hostname:port`, and
  `smtp+tls://user:pass@hostname:port`. Mandrill can also be used
  via 'mandrill://your-mandrill-api-key', though this requires the
  [djrill][] package.
* `DEFAULT_FROM_EMAIL` is the default email address to use for various
  automated correspondence from the site manager(s), such as password
  resets. Defaults to `webmaster@localhost`.
* `ADMIN_EMAIL` is the email address to send error reports to. If
  undefined, error reports will not be emailed.
* `MINIGROUP_DIGESTIF_USERPASS` is a string of the form `username:password`
  that enables the sending of Minigroup digests from external jobs. If
  empty or undefined, minigroup digest functionality will be disabled. For
  more information, see [minigroup_digestif/README.md][].
* `SECURE_PROXY_SSL_HEADER` is an optional HTTP request header field name
  and value indicating that the request is actually secure. For example,
  Heroku deployments should set this to `X-Forwarded-Proto: https`.
* `GA_TRACKING_ID` is the Google Analytics Tracking ID for your app.
  Optional.
* `GA_HOSTNAME` is the hostname of your app for Google Analytics tracking.
  It's usually the top-level domain of your app. If `GA_TRACKING_ID` is
  defined, this must be defined too.
* `SITE_ID` is the site id of the current site as used by Django's
  [sites][] framework. Defaults to `1`.
* `DISCOURSE_SSO_SECRET` is the SSO secret for Discourse single sign-on.
  For more information, see [discourse_sso/README.md][]. If empty or
  undefined, Discourse SSO functionality will be disabled.
* `DISCOURSE_SSO_ORIGIN` is the origin of your Discourse site. If
  `DISCOURSE_SSO_SECRET` is set, this must also be set.

## Flatpages

Some pages on the site are [flatpages][]. You'll want to create
flatpage records for the following URLs via the Django admin
interface, or else they will result in 404s:

* `/faq/` is the Frequently Asked Questions page.

## Multi-City Directories

By default, this project is set up to serve a directory for one Hive city.
However, it can also be configured using Django's [sites][] framework
to serve multiple directories for different cities.

To enable this functionality, you'll need to use the Django admin interface
to associate a city with your desired site. If no city is associated with
a site, then that site will serve a multi-city directory, allowing users
to explore the Hive ecosystem at large.

To illustrate, here's an example of two sites, each powered by the same
Django installation:

* **directory.hivenyc.org** offers a local-context, single-city directory
  for Hive NYC members. Its homepage looks like this:

  <img src="https://cloud.githubusercontent.com/assets/124687/3404900/8ca4c208-fd76-11e3-9c72-8ef5e37cdd5c.png" width="320">

* **directory.hivelearningnetworks.org** offers a global-context,
  multi-city directory for Hive members around the world, and for cities
  that don't have the resources to set up their own local-context directory
  site. Its homepage looks like this:

  <img src="https://cloud.githubusercontent.com/assets/124687/3404905/90aaebc0-fd76-11e3-8b08-2d4d82466a3a.png" width="320">

Clicking on the "New York City" link in the second screen-shot will take
the user to a page at `/nyc/` that looks similar (but not *identical*) to
the first screen-shot.

<!-- Links -->

  [twelve-factor]: http://12factor.net/
  [djrill]: https://github.com/brack3t/Djrill
  [minigroup_digestif/README.md]: https://github.com/toolness/hive-django/tree/master/minigroup_digestif#readme
  [discourse_sso/README.md]: https://github.com/toolness/hive-django/tree/master/discourse_sso#readme
  [flatpages]: https://docs.djangoproject.com/en/1.6/ref/contrib/flatpages/
  [sites]: https://docs.djangoproject.com/en/1.5/ref/contrib/sites/
