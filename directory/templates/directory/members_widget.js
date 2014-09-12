{% load directory %}

(function() {
  var FRAME_URL = "{{ ORIGIN }}{% city_url 'members_widget' %}";
  var script = document.scripts[document.scripts.length-1];
  var iframe = document.createElement('iframe');

  iframe.setAttribute('src', FRAME_URL);
  iframe.setAttribute('frameBorder', '0');
  script.parentNode.replaceChild(iframe, script);
  iframe.style.width = '100%';
  window.addEventListener('message', function(event) {
    if (event.source != iframe.contentWindow) return;

    var match = event.data.match(/^height:([0-9]+)$/);
    if (!match) return;

    var height = parseInt(match[1]);

    iframe.style.height = height + 'px';
  }, false);
})();
