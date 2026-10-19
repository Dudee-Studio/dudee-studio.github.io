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

/* Search is an enhancement; all guides and anchors also work without scripts. */
var helpSearch = document.getElementById('help-search');
if (helpSearch) {
  helpSearch.addEventListener('input', function () {
    var query = helpSearch.value.trim().toLocaleLowerCase(document.documentElement.lang);
    var count = 0;
    document.querySelectorAll('.help-case').forEach(function (guide) {
      var matches = !query || guide.textContent.toLocaleLowerCase(document.documentElement.lang).includes(query);
      guide.hidden = !matches;
      if (matches) count++;
    });
    document.querySelectorAll('.help-group').forEach(function (group) {
      group.hidden = !group.querySelector('.help-case:not([hidden])');
    });
    document.getElementById('help-no-results').hidden = count > 0;
  });
}
function revealHelpAnchor() {
  var id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
  var guide = document.getElementById(id);
  if (guide && guide.classList.contains('help-case')) {
    guide.open = true;
    guide.scrollIntoView({ block: 'start' });
  }
}
revealHelpAnchor();
window.addEventListener('hashchange', revealHelpAnchor);

/* Keep complete screenshots and their relative highlight together when enlarged. */
var helpViewer = document.getElementById('help-image-viewer');
if (helpViewer && typeof helpViewer.showModal === 'function') {
  var helpImageLinks = [];
  var helpImagePosition = 0;
  var helpImageTrigger;
  function showHelpImage() {
    var link = helpImageLinks[helpImagePosition];
    var frame = link.querySelector('.help-shot-frame').cloneNode(true);
    frame.querySelector('img').loading = 'eager';
    document.getElementById('help-image-stage').replaceChildren(frame);
    document.getElementById('help-image-caption').textContent = link.dataset.caption;
    document.getElementById('help-image-prev').disabled = helpImagePosition === 0;
    document.getElementById('help-image-next').disabled = helpImagePosition === helpImageLinks.length - 1;
  }
  document.querySelectorAll('.help-shot').forEach(function (link) {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      helpImageTrigger = link;
      helpImageLinks = Array.from(link.closest('.help-case').querySelectorAll('.help-shot'));
      helpImagePosition = helpImageLinks.indexOf(link);
      showHelpImage();
      helpViewer.showModal();
    });
  });
  document.getElementById('help-image-prev').addEventListener('click', function () {
    if (helpImagePosition > 0) { helpImagePosition--; showHelpImage(); }
  });
  document.getElementById('help-image-next').addEventListener('click', function () {
    if (helpImagePosition < helpImageLinks.length - 1) { helpImagePosition++; showHelpImage(); }
  });
  document.getElementById('help-image-close').addEventListener('click', function () { helpViewer.close(); });
  helpViewer.addEventListener('keydown', function (event) {
    if (event.key === 'ArrowLeft' && helpImagePosition > 0) { event.preventDefault(); helpImagePosition--; showHelpImage(); }
    if (event.key === 'ArrowRight' && helpImagePosition < helpImageLinks.length - 1) { event.preventDefault(); helpImagePosition++; showHelpImage(); }
  });
  helpViewer.addEventListener('close', function () { if (helpImageTrigger) helpImageTrigger.focus(); });
}
