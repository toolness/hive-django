(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

(function() {
  var scripts = document.getElementsByTagName('script');
  var thisScriptTag = scripts[scripts.length - 1];
  var trackingId = thisScriptTag.getAttribute('data-tracking-id');
  var hostname = thisScriptTag.getAttribute('data-hostname');

  ga('create', trackingId, hostname);
  ga('send', 'pageview');
})();
