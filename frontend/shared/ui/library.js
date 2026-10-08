/* Shared accessible navigation, dialogs and status messages. */
document.addEventListener('DOMContentLoaded', () => {
  'use strict';
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const storage = {
    get(key) { try { return localStorage.getItem(key); } catch { return null; } },
    set(key, value) { try { localStorage.setItem(key, value); return true; } catch { return false; } },
  };
  const nav = $('#workspace-navigation'), toggle = $('[data-nav-toggle]'), scrim = $('.z-nav-scrim');
  const mobile = matchMedia('(max-width:760px)');
  function closeNav(restore = true) {
    if (!nav) return;
    nav.dataset.open = 'false'; toggle.setAttribute('aria-expanded', 'false'); scrim.hidden = true;
    if (restore && mobile.matches) toggle.focus();
    nav.removeAttribute('role'); nav.removeAttribute('aria-modal');
  }
  toggle?.addEventListener('click', () => {
    nav.dataset.open = 'true'; toggle.setAttribute('aria-expanded', 'true'); scrim.hidden = false;
    nav.setAttribute('role', 'dialog'); nav.setAttribute('aria-modal', 'true'); $('[data-nav-close]', nav).focus();
  });
  $$('[data-nav-close]').forEach(button => button.addEventListener('click', () => closeNav()));
  mobile.addEventListener('change', () => closeNav(false));
  document.addEventListener('keydown', event => {
    if (nav?.dataset.open !== 'true' || !mobile.matches) return;
    if (event.key === 'Escape') { closeNav(); return; }
    if (event.key !== 'Tab') return;
    const links = $$('a[href],button', nav).filter(node => node.getClientRects().length);
    const first = links[0], last = links[links.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  $$('[data-dialog-open]').forEach(button => button.addEventListener('click', () => document.getElementById(button.dataset.dialogOpen)?.showModal()));
  $$('[data-dialog-close]').forEach(button => button.addEventListener('click', () => button.closest('dialog').close()));
  let toastTimer;
  function toast(message) {
    const node = $('.z-toast'); if (!node) return;
    clearTimeout(toastTimer); node.textContent = message; node.hidden = false;
    toastTimer = setTimeout(() => { node.hidden = true; }, 4500);
  }
  window.Zui = { storage, toast };
}, { once: true });
