window.addEventListener('load', function() {
  // http://stackoverflow.com/a/1147768
  function getPageHeight() {
    var body = document.body;
    var html = document.documentElement;

    return Math.max(body.scrollHeight, body.offsetHeight, 
                    html.clientHeight, html.scrollHeight, html.offsetHeight);
  }

  function sendPageHeight() {
    window.parent.postMessage('height:' + getPageHeight(), '*');
  }

  window.addEventListener('resize', sendPageHeight, false);
  sendPageHeight();
}, false);
