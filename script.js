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
/* A visible preview gallery selects one large player. Playback follows a click. */
var projectPlayer = document.getElementById('abgehakt-player');
if (projectPlayer) {
  document.querySelectorAll('.video-choice').forEach(function (choice) {
    choice.addEventListener('click', function (event) {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      var captions = projectPlayer.querySelector('track');
      var showCaptions = captions.track.mode === 'showing';
      projectPlayer.pause();
      projectPlayer.querySelector('source').src = choice.href;
      projectPlayer.poster = choice.dataset.poster;
      projectPlayer.setAttribute('aria-label', choice.dataset.title);
      captions.src = choice.dataset.captions;
      captions.srclang = choice.dataset.language;
      captions.label = choice.dataset.language === 'en' ? 'English' : 'Deutsch';
      document.getElementById('selected-video-title').textContent = choice.dataset.title;
      document.getElementById('selected-video-info').textContent = choice.dataset.info;
      document.querySelectorAll('.video-choice').forEach(function (other) {
        if (other === choice) other.setAttribute('aria-current', 'true');
        else other.removeAttribute('aria-current');
      });
      projectPlayer.load();
      captions.track.mode = showCaptions ? 'showing' : 'disabled';
      projectPlayer.play().catch(function () { /* Native controls remain available. */ });
      projectPlayer.focus({ preventScroll: true });
      projectPlayer.scrollIntoView({ block: 'center', behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    });
  });
}

/* Language links work without JavaScript; preserve an open section when present. */
document.querySelectorAll('[data-language-switch]').forEach(function (link) {
  if (location.hash) link.href += location.hash;
});
document.querySelectorAll('video').forEach(function (video) {
  video.addEventListener('play', function () {
    document.querySelectorAll('video').forEach(function (other) {
      if (other !== video) other.pause();
    });
  });
});
