/* Application behavior for the versioned component catalogue. No generated JavaScript. */
(() => {
  'use strict';
  const all = (selector, root = document) => [...root.querySelectorAll(selector)];
  const at = (value, path) => !path ? value : path.split('.').reduce((v, key) => v != null && typeof v === 'object' ? v[key] : undefined, value);
  const display = value => value == null ? '—' : typeof value === 'object' ? JSON.stringify(value) : String(value);
  const names = route => [...route.matchAll(/\{([A-Za-z_]\w*)\}/g)].map(match => match[1]);
  function materialize(route, values) {
    if (!route.startsWith('/') || route.startsWith('//') || /[\\\s?#<>]/.test(route)) throw Error('Invalid destination.');
    return route.replace(/\{([A-Za-z_]\w*)\}/g, (_, key) => {
      if (values[key] == null || values[key] === '') throw Error(`Missing ${key.replaceAll('_', ' ')}. Open a record first.`);
      return encodeURIComponent(values[key]);
    });
  }
  function routeValues(route) {
    const keys = names(route);
    const pattern = '^' + route.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\\\{[A-Za-z_]\w*\\\}/g, '([^/]+)') + '/?$';
    const match = location.pathname.match(new RegExp(pattern));
    return Object.fromEntries(keys.map((key, i) => [key, match ? decodeURIComponent(match[i + 1]) : window.__ZORENTIA_PREVIEW__ ? 'example-id' : undefined]));
  }
  function validate(value, schema, label) {
    const type = schema.type;
    if (type === 'object') {
      if (!value || typeof value !== 'object' || Array.isArray(value)) throw Error(`${label} must be an object.`);
      for (const key of schema.required || []) if (value[key] === undefined || value[key] === '') throw Error(`${label}: ${key} is required.`);
      for (const [key, child] of Object.entries(value)) {
        if (schema.properties?.[key]) validate(child, schema.properties[key], key);
        else if (schema.additionalProperties === false) throw Error(`${label}: unexpected ${key}.`);
      }
    } else if (type === 'array') {
      if (!Array.isArray(value)) throw Error(`${label} must be a list.`);
      if (value.length < (schema.minItems ?? 0) || value.length > (schema.maxItems ?? Infinity)) throw Error(`${label} has an invalid number of items.`);
      if (schema.uniqueItems && new Set(value.map(item => JSON.stringify(item))).size !== value.length) throw Error(`${label} must contain unique items.`);
      value.forEach(item => validate(item, schema.items || {}, label));
    } else if (type === 'integer' || type === 'number') {
      if (typeof value !== 'number' || !Number.isFinite(value) || type === 'integer' && !Number.isInteger(value)) throw Error(`${label} must be a valid ${type}.`);
      if (value < (schema.minimum ?? -Infinity) || value > (schema.maximum ?? Infinity) || value <= (schema.exclusiveMinimum ?? -Infinity) || value >= (schema.exclusiveMaximum ?? Infinity)) throw Error(`${label} is outside the allowed range.`);
      if (schema.multipleOf && Math.abs(value / schema.multipleOf - Math.round(value / schema.multipleOf)) > 1e-8) throw Error(`${label} has an invalid increment.`);
    } else if (type === 'boolean' && typeof value !== 'boolean') throw Error(`${label} must be true or false.`);
    else if (type === 'string') {
      if (typeof value !== 'string' || value.length < (schema.minLength ?? 0) || value.length > (schema.maxLength ?? Infinity)) throw Error(`${label} has an invalid length.`);
      if (schema.pattern && !new RegExp(schema.pattern).test(value)) throw Error(`${label} has an invalid format.`);
    }
    if (schema.enum && !schema.enum.some(item => JSON.stringify(item) === JSON.stringify(value))) throw Error(`${label} is not an allowed choice.`);
  }
  function formValues(form, schema) {
    const values = {};
    if (!form) return values;
    for (const input of all('[name]', form)) {
      const rules = schema.properties?.[input.name];
      if (!rules || input.disabled) continue;
      let value = input.type === 'checkbox' ? input.checked : input.value;
      if (value === '' && !(schema.required || []).includes(input.name)) continue;
      if (rules.type === 'integer' || rules.type === 'number') value = value === '' ? NaN : Number(value);
      if (rules.type === 'object' || rules.type === 'array') {
        try { value = JSON.parse(value); } catch { throw Error(`${input.name.replaceAll('_', ' ')} must contain valid JSON.`); }
      }
      if (rules.type === 'boolean' && input.type !== 'checkbox') value = value === 'true';
      if (input.type === 'datetime-local' && value) value = new Date(value).toISOString();
      validate(value, rules, input.name.replaceAll('_', ' '));
      Object.defineProperty(values, input.name, { value, enumerable: true, configurable: true });
    }
    return values;
  }
  function mount(config) {
    const start = () => {
      const actions = new Map(config.actions.map(action => [action.id, action]));
      const parameters = routeValues(config.screen_route);
      const tableState = new WeakMap();
      const disabledBefore = new WeakMap();
      const storage = window.Zui.storage;
      const region = (root, kind) => root.querySelector(`[data-${kind}-region]`);
      function show(root, kind, message) {
        const node = region(root, kind); if (!node) return;
        node.hidden = false; node.textContent = message;
        if (kind === 'error') node.focus();
      }
      function busy(root, state) {
        root.setAttribute('aria-busy', String(state));
        const indicator = region(root, 'loading'); if (indicator) indicator.hidden = !state;
        all('button,input,textarea,select', root).forEach(node => {
          if (state) { disabledBefore.set(node, node.disabled); node.disabled = true; }
          else if (disabledBefore.has(node)) { node.disabled = disabledBefore.get(node); disabledBefore.delete(node); }
        });
      }
      function links(scope, values) {
        all('[data-screen-link]', scope).forEach(link => {
          try { link.href = materialize(link.dataset.screenLink, values); link.removeAttribute('aria-disabled'); }
          catch { link.removeAttribute('href'); link.setAttribute('aria-disabled', 'true'); }
        });
      }
      links(document, parameters);
      function drawTable(node) {
        const state = tableState.get(node), options = JSON.parse(node.dataset.tableConfig);
        const { records, page, size } = state;
        const rows = records.slice(page * size, (page + 1) * size).map(record => {
          const row = node.querySelector('template').content.cloneNode(true);
          all('[data-value]', row).forEach(cell => { cell.textContent = display(at(record, cell.dataset.value)); });
          const link = row.querySelector('[data-row-link]');
          if (link) {
            const values = { ...parameters, ...record };
            const missing = names(options.row_route).filter(key => values[key] == null);
            if (missing.length === 1) values[missing[0]] = at(record, options.row_key || 'id');
            try { link.href = materialize(options.row_route, values); }
            catch { link.removeAttribute('href'); link.setAttribute('aria-disabled', 'true'); }
          }
          return row;
        });
        node.querySelector('tbody').replaceChildren(...rows);
        node.querySelector('[data-empty]').hidden = records.length !== 0;
        node.querySelector('[data-page-status]').textContent = records.length ? `${page * size + 1}–${Math.min((page + 1) * size, records.length)} of ${records.length} loaded records` : '0 records';
        node.querySelector('[data-page="-1"]').disabled = page === 0;
        node.querySelector('[data-page="1"]').disabled = (page + 1) * size >= records.length;
      }
      function render(root, payload) {
        all('[data-table-config]', root).forEach(node => {
          const options = JSON.parse(node.dataset.tableConfig), records = at(payload, options.path);
          if (!Array.isArray(records)) throw Error('The response did not contain the expected records.');
          tableState.set(node, { records: [...records], page: 0, size: options.page_size || 20, sort: null, direction: 1 });
          drawTable(node);
        });
        all('[data-value]', root).filter(node => !node.closest('[data-table-config]')).forEach(node => {
          const details = node.closest('[data-details-path]');
          node.textContent = display(at(details ? at(payload, details.dataset.detailsPath) : payload, node.dataset.value));
        });
      }
      all('[data-table-config]').forEach(node => {
        node.addEventListener('click', event => {
          const state = tableState.get(node); if (!state) return;
          const page = event.target.closest('[data-page]'), sort = event.target.closest('[data-column-sort]');
          if (page) state.page += Number(page.dataset.page);
          if (sort) {
            const key = sort.dataset.columnSort;
            state.direction = state.sort === key ? -state.direction : 1; state.sort = key; state.page = 0;
            state.records.sort((a, b) => String(at(a, key) ?? '').localeCompare(String(at(b, key) ?? ''), undefined, { numeric: true }) * state.direction);
            all('th', node).forEach(th => th.removeAttribute('aria-sort'));
            sort.closest('th').setAttribute('aria-sort', state.direction === 1 ? 'ascending' : 'descending');
          }
          if (page || sort) drawTable(node);
        });
      });
      async function request(action, values) {
        const schema = action.request_schema || {};
        validate(Object.fromEntries(Object.entries(values).filter(([key]) => Object.hasOwn(schema.properties || {}, key))), { ...schema, type: 'object' }, 'Request');
        const pathNames = names(action.route);
        const url = materialize(action.route, values);
        const data = Object.fromEntries(Object.entries(values).filter(([key]) => !pathNames.includes(key) && Object.hasOwn(schema.properties || {}, key)));
        const headers = { Accept: 'application/json' }, token = storage.get(config.storage_key);
        if (action.authentication === 'required' && !token && !window.__ZORENTIA_PREVIEW__) throw Error('Please sign in before using this action.');
        if (token) headers.Authorization = `Bearer ${token}`;
        const options = { method: action.method, headers, credentials: 'same-origin' };
        let target = url;
        if (['GET', 'HEAD'].includes(action.method)) {
          const query = new URLSearchParams();
          for (const [key, value] of Object.entries(data)) query.set(key, typeof value === 'object' ? JSON.stringify(value) : String(value));
          if (query.size) target += '?' + query;
        } else { headers['Content-Type'] = 'application/json'; options.body = JSON.stringify(data); }
        const response = await fetch(target, options);
        const payload = response.status === 204 || action.method === 'HEAD' ? {} : await response.json().catch(() => { throw Error('The server returned an unreadable response.'); });
        if (!response.ok) throw Error(typeof payload.message === 'string' ? payload.message : typeof payload.error === 'string' ? payload.error : `Request failed (${response.status}).`);
        return payload;
      }
      async function execute(root, action, prefill = false) {
        if (root.getAttribute('aria-busy') === 'true') return;
        try {
          for (const kind of ['error', 'success']) { const node = region(root, kind); if (node) node.hidden = true; }
          const form = prefill ? null : root.tagName === 'FORM' ? root : root.querySelector('form');
          if (form && !form.reportValidity()) return;
          const values = { ...parameters, ...formValues(form, action.request_schema || {}) };
          busy(root, true);
          const payload = await request(action, values);
          if (prefill) {
            const record = at(payload, root.dataset.prefillPath || '');
            all('[name]', root).forEach(input => {
              if (!record || !Object.hasOwn(record, input.name) || /password|secret|token/i.test(input.name)) return;
              if (input.type === 'checkbox') input.checked = Boolean(record[input.name]);
              else if (input.type === 'datetime-local') input.value = String(record[input.name]).slice(0, 16);
              else input.value = typeof record[input.name] === 'object' ? JSON.stringify(record[input.name], null, 2) : record[input.name] ?? '';
            });
          } else {
            if (action.token_path && !window.__ZORENTIA_PREVIEW__) {
              const token = at(payload, action.token_path);
              if (typeof token !== 'string' || !token) throw Error('The sign-in response did not contain the expected access token.');
              if (!window.__ZORENTIA_PREVIEW__ && !storage.set(config.storage_key, token)) throw Error('Browser storage is unavailable. Sign-in could not be retained.');
            }
            render(root, payload);
            show(root, 'success', ['GET', 'HEAD'].includes(action.method) ? 'Loaded.' : action.token_path ? 'Signed in.' : 'Changes saved.');
            if (action.success_route && !window.__ZORENTIA_PREVIEW__) location.assign(materialize(action.success_route, { ...values, ...payload }));
          }
        } catch (error) { show(root, 'error', error.message || 'Something went wrong. Please try again.'); }
        finally {
          busy(root, false);
          // Pagination is computed from the new response, independently of action loading.
          all('[data-table-config]', root).forEach(node => { if (tableState.has(node)) drawTable(node); });
        }
      }
      all('[data-action-id]').forEach(root => {
        const action = actions.get(root.dataset.actionId); if (!action) return;
        root.addEventListener('submit', event => { event.preventDefault(); execute(root, action); });
        root.querySelector('[data-reload]')?.addEventListener('click', () => execute(root, action));
        if (root.dataset.prefillAction) execute(root, actions.get(root.dataset.prefillAction), true);
        else if (root.dataset.autoload === 'true') execute(root, action);
      });
      all('[data-options-action]').forEach(select => {
        const form = select.closest('form'), action = actions.get(select.dataset.optionsAction);
        if (!form || !action) return;
        (async () => {
          try {
            busy(form, true);
            const payload = await request(action, parameters);
            const records = at(payload, select.dataset.optionsPath || '');
            if (!Array.isArray(records)) throw Error('The options response did not contain the expected list.');
            const choices = records.map(record => {
              const value = at(record, select.dataset.optionValuePath);
              const label = at(record, select.dataset.optionLabelPath);
              if (value == null || label == null) throw Error('An option was missing its value or label.');
              const option = document.createElement('option');
              option.value = String(value); option.textContent = String(label);
              return option;
            });
            const placeholder = document.createElement('option');
            placeholder.value = ''; placeholder.textContent = 'Choose…';
            select.replaceChildren(placeholder, ...choices);
          } catch (error) {
            select.replaceChildren(Object.assign(document.createElement('option'), { value: '', textContent: 'Options unavailable' }));
            show(form, 'error', error.message || 'Options could not be loaded.');
          } finally { busy(form, false); }
        })();
      });
      all('[data-tabs]').forEach(group => {
        const tabs = all('[role=tab]', group).filter(tab => tab.closest('[data-tabs]') === group);
        function activate(tab, focus = false) {
          tabs.forEach(item => {
            const active = item === tab; item.setAttribute('aria-selected', String(active)); item.tabIndex = active ? 0 : -1;
            document.getElementById(item.getAttribute('aria-controls')).hidden = !active;
          });
          if (focus) tab.focus();
        }
        tabs.forEach((tab, index) => {
          tab.addEventListener('click', () => activate(tab));
          tab.addEventListener('keydown', event => {
            const next = event.key === 'ArrowRight' ? (index + 1) % tabs.length : event.key === 'ArrowLeft' ? (index + tabs.length - 1) % tabs.length : event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : null;
            if (next !== null) { event.preventDefault(); activate(tabs[next], true); }
          });
        });
        if (tabs.length) activate(tabs[0]);
      });
    };
    if (document.readyState === 'complete') start();
    else document.addEventListener('DOMContentLoaded', start, { once: true });
  }
  window.ZorentiaUI = { mount };
})();
