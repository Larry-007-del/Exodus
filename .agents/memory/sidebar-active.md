---
name: Sidebar active states
description: How active nav link highlighting works in base.html
---

**Rule:** Active highlighting is done entirely in JavaScript at the bottom of `base.html` — NOT via Django template tags or `request.resolver_match`.

**Why:** HTMX partial navigation doesn't reload the full page, so a JS approach that runs on `DOMContentLoaded` is more reliable than a server-side approach.

**How it works:** The script reads `window.location.pathname`, iterates sidebar links, finds the best match (longest matching prefix), then adds classes: `bg-brand-50 text-brand-700 font-semibold ring-1 ring-brand-200/60 dark:bg-brand-950/40 dark:text-brand-300 dark:ring-brand-800/40` and removes the inactive classes.

**How to apply:** When adding new sidebar links in `base.html`, use the standard inactive link class pattern `group flex items-center rounded-xl px-2.5 py-2 ... text-gray-600 hover:bg-gray-100/80 ...`. The JS will automatically detect and highlight the active one.
