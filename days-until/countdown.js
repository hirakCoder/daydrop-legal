// Live countdowns for /days-until/ pages. Every number is computed in the visitor's own time zone,
// counting to local midnight at the start of the event day, so "days until Halloween" in Sydney and
// in Toronto are each correct for the person reading. The page's static text carries the date
// itself (for crawlers and no-JS readers); this script only fills in the live numbers.
(function () {
  'use strict';

  function startOf(dateStr) {
    var p = dateStr.split('-');
    return new Date(+p[0], +p[1] - 1, +p[2], 0, 0, 0, 0); // local midnight
  }

  function parts(ms) {
    var s = Math.max(0, Math.floor(ms / 1000));
    return {
      days: Math.floor(s / 86400),
      hours: Math.floor((s % 86400) / 3600),
      minutes: Math.floor((s % 3600) / 60),
      seconds: s % 60,
    };
  }

  // Whole calendar days left (what people mean by "days until"): today counts as 0 on the day itself.
  function calendarDays(target) {
    var now = new Date();
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    return Math.round((target - today) / 86400000);
  }

  function plural(n, word) { return n + ' ' + word + (n === 1 ? '' : 's'); }

  function render(el) {
    var target = startOf(el.getAttribute('data-target'));
    var name = el.getAttribute('data-name') || 'the day';
    var now = new Date();
    var left = target - now;
    var dayEnd = new Date(target.getTime() + 86400000);
    var big = el.querySelector('[data-days]');
    var fine = el.querySelector('[data-fine]');
    var sub = el.querySelector('[data-sub]');

    if (left > 0) {
      var p = parts(left);
      var cal = calendarDays(target);
      if (big) big.textContent = cal;
      if (sub) sub.textContent = (cal === 1 ? 'day' : 'days') + ' until ' + name;
      if (fine) fine.textContent = 'Exactly ' + plural(p.days, 'day') + ', ' + plural(p.hours, 'hour') + ', ' +
        plural(p.minutes, 'minute') + ' and ' + plural(p.seconds, 'second') +
        ' · ' + plural(Math.max(0, cal), 'sleep') + ' · about ' + plural(Math.floor(cal / 7), 'week');
    } else if (now < dayEnd) {
      if (big) big.textContent = '🎉';
      if (sub) sub.textContent = 'It’s ' + name + ' today';
      if (fine) fine.textContent = '';
    } else {
      if (big) big.textContent = '—';
      if (sub) sub.textContent = name + ' has passed';
      if (fine) fine.textContent = el.getAttribute('data-next') || '';
    }
  }

  function tick() {
    var els = document.querySelectorAll('[data-countdown]');
    for (var i = 0; i < els.length; i++) render(els[i]);
  }

  // "Popular where you are": a coarse region from the browser's time zone, no IP lookup, nothing stored.
  function region() {
    var tz = '';
    try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
    if (/^Asia\/(Kolkata|Calcutta|Kathmandu|Colombo|Dhaka|Karachi)/.test(tz)) return 'south-asia';
    if (/^Asia\/(Shanghai|Hong_Kong|Taipei|Singapore|Seoul|Tokyo|Ho_Chi_Minh|Saigon|Kuala_Lumpur|Manila|Jakarta|Macau)/.test(tz)) return 'east-asia';
    if (/^America\/(Toronto|Vancouver|Edmonton|Winnipeg|Halifax|St_Johns|Regina|Montreal)/.test(tz)) return 'canada';
    if (/^(America|US|Pacific\/Honolulu)/.test(tz)) return 'us';
    if (/^Europe\//.test(tz)) return 'europe';
    if (/^(Australia|Pacific\/Auckland)/.test(tz)) return 'oceania';
    return 'other';
  }

  function personalize() {
    var list = document.querySelector('[data-event-list]');
    if (!list) return;
    var r = region();
    var items = Array.prototype.slice.call(list.querySelectorAll('[data-regions]'));
    var now = new Date();
    items.forEach(function (it) {
      var target = startOf(it.querySelector('[data-countdown]').getAttribute('data-target'));
      var local = (it.getAttribute('data-regions') || '').split(' ').indexOf(r) !== -1;
      it.setAttribute('data-sort', String((local ? 0 : 1e13) + Math.max(0, target - now)));
      var tag = it.querySelector('[data-local]');
      if (tag) tag.hidden = !local;
    });
    items.sort(function (a, b) { return +a.getAttribute('data-sort') - +b.getAttribute('data-sort'); });
    items.forEach(function (it) { list.appendChild(it); });
  }

  personalize();
  tick();
  setInterval(tick, 1000);
})();
