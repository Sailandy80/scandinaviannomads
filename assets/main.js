(function () {
  var header = document.querySelector('.site-header');
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (document.body.classList.contains('has-overlay')) header.classList.toggle('solid', open || window.scrollY > 40);
    });
  }
  // Transparent header over photos turns solid once you scroll
  if (document.body.classList.contains('has-overlay') && header) {
    var onScroll = function () {
      header.classList.toggle('solid', window.scrollY > 40 || (nav && nav.classList.contains('open')));
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }
  // Region filter on the destinations page
  var chips = document.querySelectorAll('.chip[data-filter]');
  var grid = document.getElementById('dest-grid');
  var empty = document.getElementById('dest-empty');
  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      chips.forEach(function (c) { c.classList.remove('active'); });
      chip.classList.add('active');
      var f = chip.getAttribute('data-filter'), shown = 0;
      grid.querySelectorAll('.tile').forEach(function (card) {
        var show = f === 'all' || card.getAttribute('data-region') === f;
        card.hidden = !show;
        if (show) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    });
  });
})();
