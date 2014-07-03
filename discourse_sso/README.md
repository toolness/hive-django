The `discourse_sso` Dajngo app provides a [Discourse SSO][sso] endpoint 
for a Hive directory, allowing users to login with their Hive credentials
and use the same username that they have on the site.

To enable Discourse SSO on your site, ensure the following Django settings
are configured:

* `DISCOURSE_SSO_SECRET` is the secret shared between your Hive directory
  and the Discourse site.
* `DISCOURSE_SSO_ORIGIN` is the origin of your Discourse site, e.g.
  `http://my-discourse.org`.

On the Discourse side, you'll want to make sure the following are
configured under "Settings > Users" in Discourse's admin panel:

* "sso secret" should be identical to `DISCOURSE_SSO_SECRET`.
* "enable sso" should be checked.
* "sso url" should be set to the origin of your Hive directory, followed
  by `/discourse_sso/`. For example, `http://example.org/discourse_sso/`.
* You'll also probably want to check all the checkboxes for SSO overrides,
  so that user information on your Discourse always reflects the state
  of your Hive directory as closely as possible.

<!-- Links -->

  [sso]: https://meta.discourse.org/t/official-single-sign-on-for-discourse/13045
