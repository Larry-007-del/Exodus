---
name: CSS build required
description: Tailwind CSS must be rebuilt after template or config changes
---

**Rule:** Any new Tailwind utility class added to templates or `tailwind.config.js` won't appear in the browser until `npm run build` is run.

**Why:** The browser-served file is `static/css/styles.css` (compiled output). The source is `static/css/tailwind.css`. The build step (Tailwind JIT scan) generates `styles.css`.

**How to apply:** After editing templates or `tailwind.config.js`, run `npm run build` before restarting the workflow. The build also copies Alpine.js/HTMX/Flowbite assets.
