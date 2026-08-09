/* Theme toggle for writing/ pages. The inline <head> script has already
   applied the theme before paint; this only handles switching it. */
(function () {
    'use strict';

    var toggle = document.getElementById('themeToggle');
    if (!toggle) return;

    var meta = document.getElementById('themeColor');
    var osDark = window.matchMedia('(prefers-color-scheme: dark)');
    var COLOR = { light: '#ffffff', dark: '#17171a' };

    function stored() {
        try { return localStorage.getItem('theme'); } catch (e) { return null; }
    }

    function apply(theme, persist) {
        document.documentElement.setAttribute('data-theme', theme);
        if (meta) meta.setAttribute('content', COLOR[theme]);
        toggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
        if (!persist) return;
        try { localStorage.setItem('theme', theme); } catch (e) {}
    }

    apply(document.documentElement.getAttribute('data-theme') || 'light', false);

    toggle.addEventListener('click', function () {
        apply(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', true);
    });

    // Follow the OS only until the visitor makes an explicit choice.
    var onChange = function (e) {
        if (stored()) return;
        apply(e.matches ? 'dark' : 'light', false);
    };
    if (osDark.addEventListener) osDark.addEventListener('change', onChange);
    else if (osDark.addListener) osDark.addListener(onChange);
})();
