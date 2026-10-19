/* Videos: Trägt man bei einem Projekt data-youtube="VIDEO-ID" (11 Zeichen) oder data-video="videos/datei.mp4" ein,
   ersetzt dieses Skript den Platzhalter. YouTube wird erst nach Klick geladen (youtube-nocookie.com). */
document.querySelectorAll('.media').forEach(function (el) {
  var yt = (el.getAttribute('data-youtube') || '').trim();
  var file = (el.getAttribute('data-video') || '').trim();
  if (file) {
    var v = document.createElement('video');
    v.controls = true;
    v.preload = 'metadata';
    v.playsInline = true;
    v.src = file;
    el.textContent = '';
    el.appendChild(v);
  } else if (/^[A-Za-z0-9_-]{11}$/.test(yt)) {
    el.innerHTML = '<button class="play" type="button" aria-label="Trailer abspielen"><span class="play-ico" aria-hidden="true">▶</span><b>Trailer abspielen</b><small>Beim Abspielen werden Daten von YouTube geladen.</small></button>';
    el.querySelector('button').addEventListener('click', function () {
      el.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + yt + '?autoplay=1&rel=0" title="Trailer" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
    });
  }
});

/* Intro-Banner auf der Startseite: Hier wird später die three.js-Animation oder das Intro-Video eingebaut. */

/* Videos dürfen sich nicht gegenseitig mit Musik überlagern. */
document.querySelectorAll('.video-formats input').forEach(function (input) {
  input.addEventListener('change', function () {
    input.closest('.video-formats').querySelectorAll('video').forEach(function (video) {
      video.pause();
    });
  });
});
document.querySelectorAll('video').forEach(function (video) {
  video.addEventListener('play', function () {
    document.querySelectorAll('video').forEach(function (other) {
      if (other !== video) other.pause();
    });
  });
});
