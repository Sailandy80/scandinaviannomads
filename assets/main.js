(function () {
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  var chips = document.querySelectorAll('.chip[data-filter]');
  var grid = document.getElementById('dest-grid');
  var empty = document.getElementById('dest-empty');
  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      chips.forEach(function (c) { c.classList.remove('active'); });
      chip.classList.add('active');
      var f = chip.getAttribute('data-filter'), shown = 0;
      grid.querySelectorAll('.dest-card').forEach(function (card) {
        var show = f === 'all' || card.getAttribute('data-region') === f;
        card.style.display = show ? '' : 'none';
        if (show) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    });
  });
})();
