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
python manage.py migrate
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
* `HIVE_CITY` is the name of the city to which this Hive network
  belongs. It's used for display purposes only.
* `GA_TRACKING_ID` is the Google Analytics Tracking ID for your app.
  Optional.
* `GA_HOSTNAME` is the hostname of your app for Google Analytics tracking.
  It's usually the top-level domain of your app. If `GA_TRACKING_ID` is
  defined, this must be defined too.
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

<!-- Links -->

  [twelve-factor]: http://12factor.net/
  [djrill]: https://github.com/brack3t/Djrill
  [minigroup_digestif/README.md]: https://github.com/toolness/hive-django/tree/master/minigroup_digestif#readme
  [flatpages]: https://docs.djangoproject.com/en/1.6/ref/contrib/flatpages/
