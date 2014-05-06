The `minigroup_digestif` Django app provides a simple HTTP POST
endpoint that allows external jobs to delegate the mailing of an
HTML Minigroup digest to anyone who has opted-in.

To use it, first set `MINIGROUP_DIGESTIF_USERPASS` to a string of the form
`username:password`. The password doesn't have to be memorable, since
an automated job will be using it, so make it as unguessable as possible.

## Manual Testing

First, you'll want to create a user with a valid email address that
subscribes to the Minigroup digest. Then, run:

    curl -u username:password -d 'html=<em>testing</em>' \
    http://localhost:8000/minigroup_digestif/send -i

You should hopefully get a response that looks something like this:

    HTTP/1.0 200 OK
    Date: Tue, 06 May 2014 13:40:02 GMT

    Digest sent.

Check your email inbox; it should have received a new email.

## Integration With Node-based minigroup_digestif

Assuming your site is set up at example.org over HTTPS, set the 
`POST_URL` on your [minigroup_digestif][] job to:

    https://username:password@example.org/minigroup_digestif/send

Then run `node send-digest.js`.

<!-- Links -->

  [minigroup_digestif]: https://github.com/toolness/minigroup-digestif
