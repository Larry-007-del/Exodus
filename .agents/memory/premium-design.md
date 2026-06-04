---
name: Premium design system
description: Design tokens and approach for the premium upgrade
---

**Background:** `bg-[#f7f8fc]` light / `bg-[#0c0f1d]` dark. A single CSS radial-gradient halo overlay (not animated blobs) sits fixed behind content.

**Login page:** Deep navy `#06091a` with `radial-gradient(ellipse 130% 90% at 50% -10%, #1a1f5e, #0b0e27, #06091a)`. Card uses `backdrop-blur-2xl`, `border-white/[0.1]`, hairline top highlight.

**Sidebar:** `bg-white/90 dark:bg-[#0d1020]/95`, `border-black/[0.06] dark:border-white/[0.05]`. Nav links use `text-gray-600 hover:bg-gray-100/80 dark:text-gray-400 dark:hover:bg-gray-800/50`. Active state adds `ring-1 ring-brand-200/60 bg-brand-50 dark:bg-brand-950/40`.

**Nav bar:** `bg-white/80 backdrop-blur-xl border-black/[0.06] dark:bg-[#0c0f1d]/85 dark:border-white/[0.06]`.

**Toasts:** Dark frosted glass `bg-gray-950/95 backdrop-blur-xl`, coloured left stripe + icon per type, click-to-dismiss.

**Dashboard banner:** Deep indigo gradient (not purple blobs), subtle grid overlay at 8% opacity, reduced font weight from extrabold to bold.

**Custom shadows/animations in tailwind.config.js:** `shadow-card`, `shadow-card-hover`, `shadow-brand-glow`, `animate-shimmer`, `animate-glow-pulse`.

**Custom scrollbar:** Thin 6px indigo-tinted bar defined in `static/css/tailwind.css` `@layer base`.
