---
name: Middleware order
description: InactivityLogoutMiddleware must follow AuthenticationMiddleware
---

**Rule:** `InactivityLogoutMiddleware` accesses `request.user`, which is only populated by `AuthenticationMiddleware`. It must be listed in `MIDDLEWARE` **after** `AuthenticationMiddleware`.

**Why:** Placing it before caused `AttributeError: 'WSGIRequest' object has no attribute 'user'` on every request → 500.

**How to apply:** In `attendance_system/settings.py`, the correct order is:
1. `SessionMiddleware`
2. `CommonMiddleware`
3. `CsrfViewMiddleware`
4. `AuthenticationMiddleware`
5. `InactivityLogoutMiddleware`  ← here
6. `MessageMiddleware`
